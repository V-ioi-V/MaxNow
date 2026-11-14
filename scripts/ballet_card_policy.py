"""Private selection of active cards; never publish card IDs."""
from __future__ import annotations

import re
import threading

import book_ballet as booking
import sync_ballet as ballet

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


def select_card(source, contract):
    with _INIT_LOCK:
        if not hasattr(source, "card_policy_slots"):
            source.card_policy_slots = threading.BoundedSemaphore(2)
    with source.card_policy_slots:
        return _select_card(source, contract)


def _select_card(source, contract):
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
    if any(
        eligible.get(card_id) == "NOTOPEN"
        and card["cardStatus"] == "unactivated"
        and card["remainingClasses"] > 0
        for card_id, card in cards.items()
    ):
        raise booking.BookingFailure("activation_required")
    raise booking.BookingFailure("rules_blocked" if active else "no_eligible_card")
