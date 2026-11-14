import json
import unittest

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
    return f'<a href="/gm/weixin/my/mycardone/{ballet.STORE_ID}/{key}"><p>测试卡</p><p>{label}</p><p>有效期:{validity}</p><p>{balance}</p></a>'


class Source:
    def __init__(self, cards, blocked=()):
        self.cards = cards
        self.blocked = set(blocked)
        self.checked = []
        self.mutations = []

    def request(self, path, marker):
        assert path == ballet.MEMBERSHIP_PATH
        return "".join(card(key, **value) for key, value in self.cards.items())

    def post_fields(self, path, fields, mutation):
        if path == booking.CARD_TYPE_PATH:
            return json.dumps([{"id": key, "status": "NOTOPEN" if value.get("state") == "unactivated" else "USING"} for key,value in self.cards.items()])
        if path.startswith(booking.CHECK_RULES_PREFIX):
            self.checked.append(fields["cardid"])
            if fields["cardid"] in self.blocked:
                return json.dumps("BLOCKED")
            return json.dumps("OK")
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
            policy.select_card(source,CONTRACT)
        self.assertEqual(caught.exception.code,"unknown_result")
        self.assertEqual(source.mutations,[])

    def test_selection_requires_manual_activation(self):
        source = Source({"1":{"state":"unactivated"}})
        with self.assertRaises(booking.BookingFailure) as caught:
            policy.select_card(source,CONTRACT)
        self.assertEqual(caught.exception.code,"activation_required")
        self.assertEqual(source.mutations,[])

    def test_no_eligible_cards_fail_without_mutation(self):
        source=Source({})
        with self.assertRaises(booking.BookingFailure) as caught:
            policy.select_card(source,CONTRACT)
        self.assertEqual(caught.exception.code,"no_eligible_card")
        self.assertEqual(source.mutations,[])

    def test_execute_reports_inactive_card_without_mutation(self):
        for use_fast_path in (False, True):
            with self.subTest(fast_path=use_fast_path):
                source = FakeFastSource() if use_fast_path else BookingSource()
                original_request = source.request
                original_post = source.post_fields

                def request(path, marker):
                    if path == ballet.MEMBERSHIP_PATH:
                        return card("90002", state="unactivated")
                    return original_request(path, marker)

                def post(path, fields, mutation):
                    self.assertFalse(mutation)
                    if path == booking.CARD_TYPE_PATH:
                        return json.dumps([{"id": 90002, "status": "NOTOPEN"}])
                    return original_post(path, fields, mutation)

                source.request = request
                source.post_fields = post
                if use_fast_path:
                    release = datetime(2026, 8, 2, 14, 20, tzinfo=ballet.TIMEZONE)
                    result, _ = fast.run_fast(source, config(), {}, release, True, sleeper=lambda _: None)
                    records = result["records"]
                else:
                    result = booking.run(source, [TARGET], True)
                    records = result["data"]["records"]
                    self.assertEqual(result["status"], "preflight_failed")
                self.assertIn("activation_required", [record["status"] for record in records])
                self.assertEqual(source.mutation_count, 0)

    def test_sources_reject_card_activation_requests(self):
        for source_type in (booking.WendaBookingSource, fast.PersistentWendaBookingSource):
            source = object.__new__(source_type)
            with self.subTest(source=source_type.__name__):
                for action, fields, mutation in (
                    ("getopencardinfo", {"cardid": "1"}, False),
                    ("opencard", {}, True),
                ):
                    path = f"/gm/weixin/my/{action}/{ballet.STORE_ID}"
                    if mutation:
                        path += "/1"
                    with self.assertRaises(booking.BookingFailure) as failure:
                        source.post_fields(path, fields, mutation)
                    self.assertEqual(failure.exception.code, "configuration_error")

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
