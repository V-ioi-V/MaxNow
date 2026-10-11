import json
import tempfile
import threading
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

import ballet_card_policy as policy
import book_ballet as booking
import sync_ballet as ballet
from test_book_ballet import FakeSource as BookingSource, TARGET
from test_book_ballet_fast import FakeFastSource, config
from datetime import datetime
import book_ballet_fast as fast


def card(key, expiry="2027-02-07", remaining=4, state="active"):
    label = {"active": "使用中", "expired": "已失效", "unactivated": "未激活"}[state]
    validity = "~" if state == "unactivated" else f"2026-01-01 ~ {expiry}"
    balance = f"卡内余:{remaining}次" + ("/总50次" if state == "active" else "")
    return f'<a href="{policy.DETAIL_PREFIX}{key}"><p>测试卡</p><p>{label}</p><p>有效期:{validity}</p><p>{balance}</p></a>'


class Source:
    def __init__(self, cards, blocked=()):
        self.cards = cards
        self.blocked = set(blocked)
        self.checked = []
        self.mutations = []
        self.unknown = False
        self.activation_attempted = False

    def request(self, path, marker):
        assert path == ballet.MEMBERSHIP_PATH
        return "".join(card(key, **value) for key, value in self.cards.items())

    def request_card_detail(self, path):
        key = path.rsplit("/", 1)[-1]
        return (f'<button class="notopencard" cardid="{key}">激活</button>'
            f'<script>$.ajax({{url:"{policy.INFO_PATH}",type:"post",data:{{"cardid":cardid}}}});'
            f'$.ajax({{url:"{policy.ACTIVATE_PREFIX}"+cardid,type:"post"}});</script>')

    def post_fields(self, path, fields, mutation):
        if path == booking.CARD_TYPE_PATH:
            return json.dumps([{"id": key, "status": "NOTOPEN" if value.get("state") == "unactivated" else "USING"} for key,value in self.cards.items()])
        if path.startswith(booking.CHECK_RULES_PREFIX):
            self.checked.append(fields["cardid"])
            if fields["cardid"] in self.blocked:
                return json.dumps("BLOCKED")
            return json.dumps("OK")
        if path == policy.INFO_PATH:
            return "2027-12-31"
        if path.startswith(policy.ACTIVATE_PREFIX):
            assert mutation and fields == {}
            key = path.rsplit("/", 1)[-1]
            self.mutations.append(key)
            if self.unknown:
                raise booking.BookingFailure("unknown_result")
            self.cards[key].update(state="active", expiry="2027-12-31")
            return ""
        raise AssertionError(path)


CONTRACT = {"courseDate":"2026-10-18", "courseId":"10", "classTableId":"11", "customerId":"12", "cardTypePath":booking.CARD_TYPE_PATH, "rulesPath":booking.CHECK_RULES_PREFIX+"12"}


class CardPolicyTests(unittest.TestCase):
    def test_expiry_then_remaining_and_rule_fallback(self):
        source = Source({"3":{"expiry":"2027-04-10"}, "2":{"remaining":5}, "1":{"remaining":2}}, blocked={"1","2"})
        self.assertEqual(policy.select_card(source, CONTRACT), "3")
        self.assertEqual(source.checked, ["1","2","3"])
        self.assertEqual(source.mutations, [])

    def test_expired_empty_and_course_outside_validity_are_skipped(self):
        source = Source({"1":{"state":"expired"}, "2":{"remaining":0}, "3":{"expiry":"2026-10-17"}, "4":{}})
        self.assertEqual(policy.select_card(source, CONTRACT), "4")
        self.assertEqual(source.checked, ["4"])

    def test_unknown_rule_response_cannot_trigger_card_fallback(self):
        source = Source({"1":{},"2":{}})
        original = source.post_fields
        def post(path,fields,mutation):
            if path.startswith(booking.CHECK_RULES_PREFIX):
                raise booking.BookingFailure("unknown_result")
            return original(path,fields,mutation)
        source.post_fields = post
        with self.assertRaises(booking.BookingFailure) as caught:
            policy.select_card(source,CONTRACT,True)
        self.assertEqual(caught.exception.code,"unknown_result")
        self.assertEqual(source.mutations,[])

    def test_dry_run_does_not_activate(self):
        source = Source({"1":{"state":"unactivated"}})
        with self.assertRaises(booking.BookingFailure) as caught:
            policy.select_card(source,CONTRACT)
        self.assertEqual(caught.exception.code,"activation_required")
        self.assertEqual(source.mutations,[])

    def test_smallest_inactive_is_activated_and_requeried(self):
        source = Source({"1":{"state":"unactivated","remaining":40},"2":{"state":"unactivated","remaining":10}})
        with tempfile.TemporaryDirectory() as directory, patch.object(policy,"activation_lock",lambda d:nullcontext()):
            source.card_policy_directory = Path(directory)
            self.assertEqual(policy.select_card(source,CONTRACT,True),"2")
            self.assertEqual(source.mutations,["2"])
            self.assertEqual(json.loads((Path(directory)/"activation.json").read_text())["status"],"verified")
            self.assertEqual(policy.select_card(source,CONTRACT,True),"2")
            self.assertEqual(source.mutations,["2"])

    def test_activation_unknown_survives_process_restart(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(policy,"activation_lock",lambda d:nullcontext()):
            for attempt in range(2):
                source=Source({"1":{"state":"unactivated"}})
                source.unknown=True
                source.card_policy_directory=Path(directory)
                with self.assertRaises(booking.BookingFailure) as caught:
                    policy.select_card(source,CONTRACT,True)
                self.assertEqual(caught.exception.code,"activation_unknown")
                self.assertEqual(len(source.mutations),1 if attempt==0 else 0)

    def test_no_second_activation_when_first_card_rules_still_block(self):
        source=Source({"1":{"state":"unactivated","remaining":10},"2":{"state":"unactivated","remaining":40}},blocked={"1"})
        with tempfile.TemporaryDirectory() as directory, patch.object(policy,"activation_lock",lambda d:nullcontext()):
            source.card_policy_directory=Path(directory)
            with self.assertRaises(booking.BookingFailure):
                policy.select_card(source,CONTRACT,True)
            with self.assertRaises(booking.BookingFailure) as caught:
                policy.select_card(source,CONTRACT,True)
            self.assertEqual(caught.exception.code,"activation_limit")
            self.assertEqual(source.mutations,["1"])

    def test_activation_requires_exact_button_and_contract(self):
        source=Source({"1":{"state":"unactivated"}})
        with self.assertRaises(booking.BookingFailure):
            policy.activation_contract(source.request_card_detail(policy.DETAIL_PREFIX+"1"),"2")

    def test_no_eligible_cards_fail_without_mutation(self):
        source=Source({})
        with self.assertRaises(booking.BookingFailure) as caught:
            policy.select_card(source,CONTRACT,True)
        self.assertEqual(caught.exception.code,"no_eligible_card")
        self.assertEqual(source.mutations,[])

    def test_malformed_journal_blocks_activation(self):
        source=Source({"1":{"state":"unactivated"}})
        with tempfile.TemporaryDirectory() as directory, patch.object(policy,"activation_lock",lambda d:nullcontext()):
            source.card_policy_directory=Path(directory)
            (Path(directory)/"activation.json").write_text("broken")
            with self.assertRaises(booking.BookingFailure) as caught:
                policy.select_card(source,CONTRACT,True)
            self.assertEqual(caught.exception.code,"activation_unknown")
            self.assertEqual(source.mutations,[])

    def test_concurrent_activation_serializes_and_posts_once(self):
        source=Source({"1":{"state":"unactivated"}})
        lock=threading.RLock()
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as directory, patch.object(policy,"activation_lock",lambda d:lock):
            source.card_policy_directory=Path(directory)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda _:policy.select_card(source,CONTRACT,True),range(2)))
            self.assertEqual(results,["1","1"])
            self.assertEqual(source.mutations,["1"])

    def test_normal_booking_uses_second_card_and_single_mutation(self):
        source=BookingSource(); original_request=source.request; original_post=source.post_fields
        source.request=lambda p,m: card("90002")+card("90003",expiry="2027-04-10") if p==ballet.MEMBERSHIP_PATH else original_request(p,m)
        def post(p,fields,mutation):
            if p==booking.CARD_TYPE_PATH:
                return json.dumps([{"id":90002,"status":"USING"},{"id":90003,"status":"USING"}])
            if p.startswith(booking.CHECK_RULES_PREFIX) and fields["cardid"]=="90002":
                return json.dumps("BLOCKED")
            return original_post(p,fields,mutation)
        source.post_fields=post
        result=booking.run(source,[TARGET],True)
        self.assertEqual(result["status"],"success")
        self.assertEqual(source.last_post[1]["cardid"],"90003")
        self.assertEqual(source.mutation_count,1)
        self.assertNotIn("90003",json.dumps(result))

    def test_fast_path_rechecks_card_after_prefetch(self):
        source=FakeFastSource(); original_request=source.request; original_post=source.post_fields
        source.request=lambda p,m: card("90002")+card("90003",expiry="2027-04-10") if p==ballet.MEMBERSHIP_PATH else original_request(p,m)
        submitted=[]
        def post(p,fields,mutation):
            if p==booking.CARD_TYPE_PATH:
                return json.dumps([{"id":90002,"status":"USING"},{"id":90003,"status":"USING"}])
            if p.startswith(booking.CHECK_RULES_PREFIX) and fields["cardid"]=="90002" and source.mutation_count:
                return json.dumps("BLOCKED")
            if mutation: submitted.append(fields["cardid"])
            return original_post(p,fields,mutation)
        source.post_fields=post
        release=datetime(2026,8,2,14,20,tzinfo=ballet.TIMEZONE)
        result,state=fast.run_fast(source,config(),{},release,True,sleeper=lambda _:None)
        self.assertTrue(submitted)
        self.assertEqual(submitted[0],"90002")
        self.assertTrue(all(key=="90003" for key in submitted[1:]))
        self.assertEqual(source.max_active_mutation,1)


if __name__=="__main__": unittest.main()
