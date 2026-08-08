import json
import unittest

import cancel_ballet as cancellation
import sync_ballet as ballet
from test_sync_ballet import detail_html, index_html


TARGET = {
    "date": "2026-08-16",
    "startTime": "20:00",
    "endTime": "21:30",
    "courseName": "芭蕾L1-入门",
    "teacher": "王嘉豪",
    "venue": "大教室",
}
SOURCE_ID = "90001"


def cancellation_detail(source_id=SOURCE_ID, include_control=True):
    control = '<button class="cancelbook">取消预约</button>' if include_control else ""
    script = (
        "<script>"
        '$(".cancelbook").on("click",function(){'
        "$.ajax({"
        f'url:"{ballet.BASE_URL}{cancellation.CHECK_CANCEL_PREFIX}{source_id}",'
        'type:"post",async:false,success:function(r){'
        "check=JSON.parse(r);if(check=='OK'){"
        "$.ajax({"
        f'url:"{ballet.BASE_URL}{cancellation.CANCEL_SUBMIT_PATH}",'
        f'type:"post",data:{{"bookid":{source_id}}},success:function(){{'
        f'location.assign("{ballet.BASE_URL}{cancellation.CANCEL_SUCCESS_PATH}");'
        "}});}}});});"
        "</script>"
    )
    return detail_html(
        course=TARGET["courseName"],
        day=TARGET["date"],
        time_text=f'{TARGET["startTime"]}~{TARGET["endTime"]}',
        teacher=TARGET["teacher"],
        status="已预约",
        cancel_rule="课前2小时前可取消",
    ).replace("测试教室", TARGET["venue"]).replace(
        "</body>", f"{control}{script}</body>"
    )


class FakeSource:
    def __init__(self):
        self.request_count = 0
        self.post_count = 0
        self.mutation_count = 0
        self.active = True
        self.duplicate = False
        self.rules_blocked = False
        self.mutation_removes = True
        self.raise_after_mutation = False

    def request(self, path, expected_marker):
        self.request_count += 1
        if path == ballet.BOOKING_PATH:
            rows = []
            if self.active:
                rows.append(
                    (
                        SOURCE_ID,
                        TARGET["courseName"],
                        TARGET["date"],
                        "已预约",
                    )
                )
                if self.duplicate:
                    rows.append(
                        (
                            "90002",
                            TARGET["courseName"],
                            TARGET["date"],
                            "已预约",
                        )
                    )
            return index_html("约课记录", rows)
        if "/bookrecordone/" in path:
            return cancellation_detail(path.rsplit("/", 1)[-1])
        raise AssertionError(path)

    def post_fields(self, path, fields, mutation, referer):
        self.request_count += 1
        self.post_count += 1
        self.last_post = (path, dict(fields), mutation, referer)
        if path.startswith(cancellation.CHECK_CANCEL_PREFIX) and not mutation:
            return json.dumps("BLOCKED" if self.rules_blocked else "OK")
        if path == cancellation.CANCEL_SUBMIT_PATH and mutation:
            self.mutation_count += 1
            if self.mutation_removes:
                self.active = False
            if self.raise_after_mutation:
                raise cancellation.CancellationFailure("unknown_result")
            return ""
        raise AssertionError((path, fields, mutation, referer))


class BalletCancellationTests(unittest.TestCase):
    def request_payload(self, confirm):
        return json.dumps({"course": TARGET, "confirm": confirm})

    def test_execute_requires_explicit_confirmation(self):
        with self.assertRaises(cancellation.CancellationFailure) as caught:
            cancellation.parse_request(self.request_payload(False), execute=True)
        self.assertEqual(caught.exception.code, "confirmation_required")

    def test_dry_run_checks_rules_without_mutation(self):
        source = FakeSource()
        result = cancellation.run(source, TARGET, execute=False)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["records"][0]["status"], "ready")
        self.assertEqual(result["mutationAttempts"], 0)
        self.assertEqual(source.post_count, 1)

    def test_execute_posts_once_and_verifies_absence(self):
        source = FakeSource()
        result = cancellation.run(source, TARGET, execute=True)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["mutated"])
        self.assertEqual(result["mutationAttempts"], 1)
        self.assertEqual(result["data"]["records"][0]["status"], "cancelled")
        self.assertEqual(source.mutation_count, 1)
        serialized = json.dumps(result)
        self.assertNotIn(SOURCE_ID, serialized)
        self.assertNotIn(ballet.STORE_ID, serialized)

    def test_unknown_mutation_is_not_retried(self):
        source = FakeSource()
        source.mutation_removes = False
        source.raise_after_mutation = True
        result = cancellation.run(source, TARGET, execute=True)
        self.assertEqual(result["status"], "stopped")
        self.assertFalse(result["live"])
        self.assertIsNone(result["mutated"])
        self.assertEqual(result["mutationAttempts"], 1)
        self.assertEqual(
            result["data"]["records"][0]["status"], "unknown_result"
        )

    def test_unknown_transport_but_absent_is_verified_cancelled(self):
        source = FakeSource()
        source.raise_after_mutation = True
        result = cancellation.run(source, TARGET, execute=True)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mutationAttempts"], 1)
        self.assertEqual(result["data"]["records"][0]["status"], "cancelled")

    def test_not_booked_fails_closed_without_post(self):
        source = FakeSource()
        source.active = False
        result = cancellation.run(source, TARGET, execute=False)
        self.assertEqual(result["status"], "preflight_failed")
        self.assertEqual(result["data"]["records"][0]["status"], "not_booked")
        self.assertEqual(result["postsMade"], 0)

    def test_rule_block_prevents_mutation(self):
        source = FakeSource()
        source.rules_blocked = True
        result = cancellation.run(source, TARGET, execute=True)
        self.assertEqual(result["status"], "preflight_failed")
        self.assertEqual(
            result["data"]["records"][0]["status"], "cancellation_blocked"
        )
        self.assertEqual(result["mutationAttempts"], 0)

    def test_duplicate_exact_bookings_fail_closed(self):
        source = FakeSource()
        source.duplicate = True
        with self.assertRaises(cancellation.CancellationFailure) as caught:
            cancellation.run(source, TARGET, execute=False)
        self.assertEqual(caught.exception.code, "source_changed")
        self.assertEqual(source.post_count, 0)

    def test_contract_requires_live_cancel_control(self):
        path = f"/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/{SOURCE_ID}"
        with self.assertRaises(cancellation.CancellationFailure) as caught:
            cancellation.cancellation_contract(
                cancellation_detail(include_control=False),
                SOURCE_ID,
                path,
            )
        self.assertEqual(caught.exception.code, "source_changed")
        self.assertEqual(caught.exception.diagnostic["cancelControlCount"], 0)


if __name__ == "__main__":
    unittest.main()
