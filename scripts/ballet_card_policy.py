"""Private card selection and single-shot activation; never publish card IDs."""
from __future__ import annotations

import html
import json
import os
import re
import threading
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import book_ballet as booking
import sync_ballet as ballet

DETAIL_PREFIX = f"/gm/weixin/my/mycardone/{ballet.STORE_ID}/"
INFO_PATH = f"/gm/weixin/my/getopencardinfo/{ballet.STORE_ID}"
ACTIVATE_PREFIX = f"/gm/weixin/my/opencard/{ballet.STORE_ID}/"
STATE_DIR = Path("/var/lib/maxnow-ballet-card-policy")
_INIT_LOCK = threading.Lock()


class BoundCardParser(ballet.MembershipCardParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_endtag(self, tag):
        path = self.current_href
        before = len(self.cards)
        super().handle_endtag(tag)
        if len(self.cards) > before:
            self.ids.append(path.rsplit("/", 1)[-1])


def inventory(source):
    text = source.request(ballet.MEMBERSHIP_PATH, "我的会员卡")
    parser = BoundCardParser()
    parser.feed(text)
    cards = ballet.parse_membership(text)
    if len(cards) != len(parser.ids) or len(set(parser.ids)) != len(parser.ids):
        raise booking.BookingFailure("source_changed")
    return {card_id: card for card_id, card in zip(parser.ids, cards)}


def applicable(source, contract):
    rows = booking.response_json(source.post_fields(
        contract["cardTypePath"], {"courseid": contract["courseId"],
        "customerid": contract["customerId"], "shopid": ballet.STORE_ID}, mutation=False))
    if not isinstance(rows, list):
        raise booking.BookingFailure("source_changed")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise booking.BookingFailure("source_changed")
        card_id = str(row.get("id", ""))
        if not re.fullmatch(r"[1-9][0-9]{0,19}", card_id) or card_id in result:
            raise booking.BookingFailure("source_changed")
        if row.get("status") not in {"USING", "OPEN", "NOTOPEN"}:
            raise booking.BookingFailure("source_changed")
        result[card_id] = row["status"]
    return result


def activation_contract(text, card_id):
    # Bind the actual button to this card, then validate the official POST script.
    class Controls(booking.HTMLParser):
        found = False
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if "notopencard" in (values.get("class") or "").split():
                if values.get("cardid") == card_id:
                    self.found = True
    parser = Controls()
    parser.feed(text)
    scripts = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", text, re.S | re.I))
    if (not parser.found or INFO_PATH not in scripts or ACTIVATE_PREFIX not in scripts
        or not re.search(r'type\s*:\s*[\"\']post[\"\']', scripts, re.I)
        or not re.search(r'[\"\']cardid[\"\']\s*:\s*cardid', scripts)
        or not re.search(re.escape(ACTIVATE_PREFIX) + r'[\"\']\s*\+\s*cardid', scripts)):
        raise booking.BookingFailure("source_changed")


@contextmanager
def activation_lock(directory):
    import fcntl  # production Linux; tests can replace the journal/lock boundary
    try:
        descriptor = os.open(directory / "activation.lock", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o660)
        os.fchmod(descriptor, 0o660)
    except FileExistsError:
        descriptor = os.open(directory / "activation.lock", os.O_RDWR)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def save_journal(path, state):
    import tempfile
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix="activation-")
    try:
        os.chmod(name, 0o660)
        with os.fdopen(descriptor, "w") as output:
            json.dump(state, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
        if hasattr(os, "O_DIRECTORY"):
            parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def activate_one(source, card_id):
    directory = getattr(source, "card_policy_directory", STATE_DIR)
    path = directory / "activation.json"
    with activation_lock(directory):
        cards = inventory(source)
        if cards.get(card_id, {}).get("cardStatus") == "active":
            return
        if getattr(source, "activation_attempted", False):
            raise booking.BookingFailure("activation_limit")
        try:
            journal = json.loads(path.read_text()) if path.exists() else {}
        except (OSError, ValueError):
            raise booking.BookingFailure("activation_unknown") from None
        if not isinstance(journal, dict) or (journal and journal.get("status") not in {"attempted", "verified"}):
            raise booking.BookingFailure("activation_unknown")
        if journal.get("status") == "attempted":
            if cards.get(journal.get("cardId"), {}).get("cardStatus") == "active":
                save_journal(path, {**journal, "status": "verified"})
            raise booking.BookingFailure("activation_unknown")
        if cards.get(card_id, {}).get("cardStatus") != "unactivated":
            raise booking.BookingFailure("source_changed")
        detail = source.request_card_detail(DETAIL_PREFIX + card_id)
        activation_contract(detail, card_id)
        expiry = source.post_fields(INFO_PATH, {"cardid": card_id}, mutation=False).strip().strip('"')
        if expiry == "NOSELLCARD":
            raise booking.BookingFailure("activation_unavailable")
        if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", expiry):
            raise booking.BookingFailure("source_changed")
        date.fromisoformat(expiry)
        source.activation_attempted = True
        save_journal(path, {"cardId": card_id, "status": "attempted"})
        try:
            source.post_fields(ACTIVATE_PREFIX + card_id, {}, mutation=True)
            verified = inventory(source).get(card_id, {})
            if (verified.get("cardStatus") != "active"
                or verified.get("validThrough") != expiry):
                raise booking.BookingFailure("activation_unknown")
        except (booking.BookingFailure, ballet.SyncFailure):
            raise booking.BookingFailure("activation_unknown") from None
        save_journal(path, {"cardId": card_id, "status": "verified"})


def select_card(source, contract, allow_activation=False):
    with _INIT_LOCK:
        if not hasattr(source, "card_policy_slots"):
            source.card_policy_slots = threading.BoundedSemaphore(2)
    with source.card_policy_slots:
        return _select_card(source, contract, allow_activation)


def _select_card(source, contract, allow_activation=False):
    eligible = applicable(source, contract)
    cards = inventory(source)
    if any(card_id not in cards for card_id in eligible):
        raise booking.BookingFailure("source_changed")
    target_date = contract["courseDate"]
    active = [card_id for card_id, card in cards.items() if card_id in eligible
        and eligible[card_id] in {"USING", "OPEN"} and card["cardStatus"] == "active"
        and card["remainingClasses"] > 0 and card["validFrom"] <= target_date <= card["validThrough"]]
    active.sort(key=lambda key: (cards[key]["validThrough"], cards[key]["remainingClasses"], key))
    for card_id in active:
        try:
            booking.check_rules(source, contract, card_id)
            return card_id
        except booking.BookingFailure as failure:
            if failure.code != "rules_blocked":
                raise
    inactive = [key for key, card in cards.items() if key in eligible
        and eligible[key] == "NOTOPEN" and card["cardStatus"] == "unactivated"
        and card["remainingClasses"] > 0]
    inactive.sort(key=lambda key: (cards[key]["remainingClasses"], key))
    if inactive:
        if not allow_activation:
            raise booking.BookingFailure("activation_required")
        activate_one(source, inactive[0])
        return _select_card(source, contract, allow_activation=False)
    raise booking.BookingFailure("rules_blocked" if active else "no_eligible_card")
