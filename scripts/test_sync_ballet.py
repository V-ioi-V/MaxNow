import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import sync_ballet as ballet


SESSION = "a" * 32
USER_AGENT = "Synthetic-WeChat-Fixture-Agent/1.0"
NOW = datetime.fromisoformat("2026-07-27T00:17:00+08:00")


def detail_html(
    *,
    course: str,
    day: str,
    time_text: str = "10:00~11:30",
    teacher: str = "测试老师",
    status: str = "已上课",
    cancel_rule: str = "课前11小时前可取消",
) -> str:
    fields = (
        ("课程名称", course),
        ("课程日期", f"{day} 周日"),
        ("课程时间", time_text),
        ("教师名称", teacher),
        ("场地名称", "测试教室"),
        ("门店名称", "测试芭蕾工作室"),
        ("预约状态", status),
        ("取消时间", cancel_rule),
    )
    cells = "".join(
        (
            '<div class="weui-cell">'
            f'<div class="weui-cell__bd"><p>{label}</p></div>'
            f'<div class="weui-cell__ft">{value}</div>'
            "</div>"
        )
        for label, value in fields
    )
    return f"<html><title>约课记录明细</title><body>{cells}</body></html>"


def index_html(title: str, rows: list[tuple[str, str, str, str]]) -> str:
    links = "".join(
        (
            f'<a class="weui-cell" href="{ballet.BASE_URL}'
            f'/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/{source_id}">'
            f'<div class="weui-cell__bd"><p>{course}</p></div>'
            f'<div class="weui-cell__ft">{status} {day}</div>'
            "</a>"
        )
        for source_id, course, day, status in rows
    )
    count = f"，共{len(rows)}次" if title == "上课记录" else ""
    return (
        f"<html><title>{title}</title><body>"
        f'<div class="weui-cells__title">测试账号的{title}{count}</div>'
        f'<div id="list">{links}</div></body></html>'
    )


def membership_html() -> str:
    return (
        "<html><title>我的会员卡</title><body>"
        f'<a href="/gm/weixin/my/mycardone/{ballet.STORE_ID}/90001">'
        "<strong>半年卡-40次</strong>"
        "<span>有效期 : 2026-07-26~2027-01-23</span>"
        "<span>卡内余 : 39 次 / 总40 次</span>"
        "</a></body></html>"
    )


def timetable_html(
    *,
    course: str = "芭蕾L1-入门",
    time_text: str = "19:45 ~ 21:15",
    teacher: str = "测试老师",
    venue: str = "测试教室",
    status: str = "6 / 12 (满4人开班)",
) -> str:
    return (
        "<html><title>课程表</title><body>"
        '<div class="swiper-container dateswiper">'
        '<div class="swiper-slide dateslide" date="2026-07-27">7/27 周一</div>'
        '<div class="swiper-slide dateslide" date="2026-07-28">7/28 周二</div>'
        "</div>"
        '<div class="classtable">'
        f'<div class="timelinear"><p><b>{time_text}</b></p></div>'
        f'<div class="coursediv"><p><b>{course}</b></p></div>'
        f'<div class="row small"><div class="col-12">★ {teacher}'
        f'<div class="col-12 row3">{status}</div></div></div>'
        '<div class="card card-body">'
        '<div class="row form_row small"><div class="col-3">老师/教练</div>'
        f'<div class="col-9">{teacher}</div></div>'
        '<div class="row form_row small"><div class="col-3">教室/场地</div>'
        f'<div class="col-9">{venue}</div></div>'
        "</div></div></body></html>"
    )


def write_fixture(root: Path) -> None:
    rows = [
        ("10001", "芭蕾L1.5", "2026-07-26", ""),
        ("10002", "软开专项【前后腿】", "2026-06-01", ""),
    ]
    (root / "details").mkdir(parents=True)
    (root / "timetable").mkdir(parents=True)
    (root / "attendance.html").write_text(
        index_html("上课记录", rows), encoding="utf-8"
    )
    (root / "booking.html").write_text(
        index_html(
            "约课记录",
            [("10003", "芭蕾L2", "2026-08-02", "已预约")],
        ),
        encoding="utf-8",
    )
    (root / "membership.html").write_text(
        membership_html(),
        encoding="utf-8",
    )
    (root / "timetable" / "default.html").write_text(
        timetable_html(),
        encoding="utf-8",
    )
    (root / "details" / "10001.html").write_text(
        detail_html(course="芭蕾L1.5", day="2026-07-26"),
        encoding="utf-8",
    )
    (root / "details" / "10002.html").write_text(
        detail_html(
            course="软开专项【前后腿】",
            day="2026-06-01",
            time_text="11:30~12:30",
        ),
        encoding="utf-8",
    )
    (root / "details" / "10003.html").write_text(
        detail_html(
            course="芭蕾L2",
            day="2026-08-02",
            time_text="17:30~19:00",
            status="已预约",
        ),
        encoding="utf-8",
    )


class AuthFailureSource:
    session_rotated = False
    request_count = 0

    def request(self, path, expected_marker):
        self.request_count += 1
        raise ballet.SyncFailure("auth_required")


class BalletSyncTests(unittest.TestCase):
    def test_allowlist_contains_only_read_paths(self):
        accepted = (
            ballet.ATTENDANCE_PATH,
            ballet.BOOKING_PATH,
            ballet.MEMBERSHIP_PATH,
            f"/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/12345",
            f"{ballet.TIMETABLE_PATH}/2026-07-28",
        )
        for path in accepted:
            self.assertEqual(ballet.validate_read_only_path(path), path)
        rejected = (
            f"/gm/weixin/classtable/do_addbook/{ballet.STORE_ID}",
            f"/gm/weixin/my/do_cancel/{ballet.STORE_ID}",
            ballet.ATTENDANCE_PATH + "?customerid=1",
            f"/gm/weixin/my/bookrecordone/{ballet.STORE_ID}/abc",
            f"/gm/weixin/my/bookrecordone/54115/123",
            f"{ballet.TIMETABLE_PATH}/2026-7-28",
            f"{ballet.TIMETABLE_PATH}/2026-07-28?customerid=1",
        )
        for path in rejected:
            with self.subTest(path=path), self.assertRaises(ballet.SyncFailure):
                ballet.validate_read_only_path(path)

    def test_credentials_are_minimal_and_never_logged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.json"
            path.write_text(
                json.dumps(
                    {"PHPSESSID": SESSION, "user_agent": USER_AGENT}
                ),
                encoding="utf-8",
            )
            if os.name != "nt":
                path.chmod(0o600)
            credentials = ballet.load_credentials(path)
            self.assertEqual(credentials.session_id, SESSION)
            self.assertEqual(credentials.user_agent, USER_AGENT)
            if os.name != "nt":
                path.chmod(0o440)
                self.assertEqual(
                    ballet.load_credentials(path).session_id, SESSION
                )

            if os.name != "nt":
                path.chmod(0o600)
            path.write_text(
                json.dumps(
                    {
                        "PHPSESSID": SESSION,
                        "user_agent": USER_AGENT,
                        "Cookie": "not-allowed",
                    }
                ),
                encoding="utf-8",
            )
            if os.name != "nt":
                path.chmod(0o600)
            with self.assertRaises(ballet.SyncFailure):
                ballet.load_credentials(path)

    def test_auth_retry_stays_blocked_until_credential_version_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version_path = root / "credential-version"
            version_path.write_text("generation-1\n", encoding="utf-8")
            if os.name != "nt":
                version_path.chmod(0o400)
            self.assertEqual(
                ballet.load_credential_version(version_path),
                "generation-1",
            )

            state_path = root / "sync-state.json"
            state = ballet.empty_sync_state()
            state.update(
                {
                    "lastAttemptStatus": "auth_required",
                    "credentialVersion": "generation-1",
                }
            )
            state_path.write_text(json.dumps(state), encoding="utf-8")
            self.assertTrue(
                ballet.auth_retry_is_blocked(state_path, "generation-1")
            )
            self.assertFalse(
                ballet.auth_retry_is_blocked(state_path, "generation-2")
            )

    def test_classification_is_two_dimensional_and_l15_precedes_l1(self):
        self.assertEqual(
            ballet.classify_course("芭蕾 L1.5 基础"),
            ("ballet", "L1.5"),
        )
        self.assertEqual(
            ballet.classify_course("软开专项【前后腿】"),
            ("soft_open", "none"),
        )
        self.assertEqual(
            ballet.classify_course("肌肉素质 L2"),
            ("conditioning", "L2"),
        )
        self.assertEqual(
            ballet.classify_course("芭蕾 L5 进阶"),
            ("ballet", "L5"),
        )

    def test_waitlist_detail_status_with_queue_position_is_included(self):
        detail = ballet.parse_detail(
            detail_html(
                course="芭蕾L1-入门",
                day="2026-08-01",
                status="等候中, 排队序号 4",
            ),
            "10004",
        )
        normalized = ballet.normalize_upcoming(detail)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized["bookingStatus"], "waitlist")
        self.assertEqual(normalized["waitlistPosition"], 4)

    def test_relative_cancellation_rule_becomes_an_absolute_deadline(self):
        detail = ballet.parse_detail(
            detail_html(
                course="芭蕾L1-入门",
                day="2026-08-01",
                time_text="10:00~11:30",
                status="已预约",
                cancel_rule="课前11小时前可取消",
            ),
            "10005",
        )
        normalized = ballet.normalize_upcoming(detail)
        self.assertEqual(normalized["cancelRuleText"], "课前11小时前可取消")
        self.assertEqual(normalized["cancelHoursBefore"], 11)
        self.assertEqual(
            normalized["cancelDeadlineAt"],
            "2026-07-31T23:00+08:00",
        )

        fallback = ballet.parse_cancellation_rule(
            "请咨询老师",
            "2026-08-01",
            "10:00",
        )
        self.assertEqual(fallback["cancelRuleText"], "请咨询老师")
        self.assertIsNone(fallback["cancelDeadlineAt"])

    def test_membership_card_is_parsed_without_private_identifier(self):
        cards = ballet.parse_membership(membership_html())
        self.assertEqual(
            cards,
            [
                {
                    "name": "半年卡-40次",
                    "validFrom": "2026-07-26",
                    "validThrough": "2027-01-23",
                    "remainingClasses": 39,
                    "totalClasses": 40,
                    "usedClasses": 1,
                }
            ],
        )

    def test_timetable_course_is_parsed_into_safe_fields(self):
        parsed = ballet.parse_timetable(
            timetable_html(
                course="软开专项【胯】",
                time_text="18:45 ~ 19:45",
                teacher="王老师",
                venue="大教室",
                status="17 / 10 (满4人开班) 排队Wait8",
            ),
            "2026-08-01",
        )
        self.assertEqual(parsed["selectorDates"], ["2026-07-27", "2026-07-28"])
        self.assertEqual(
            parsed["records"],
            [
                {
                    "courseName": "软开专项【胯】",
                    "courseType": "soft_open",
                    "level": "none",
                    "startTime": "18:45",
                    "endTime": "19:45",
                    "durationMinutes": 60,
                    "teacher": "王老师",
                    "venue": "大教室",
                    "bookedCount": 17,
                    "capacity": 10,
                    "availability": "queue_available",
                    "date": "2026-08-01",
                }
            ],
        )

    def test_sunday_publish_window_keeps_today_and_adds_next_week(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            write_fixture(fixture)
            snapshot = ballet.build_timetable_snapshot(
                ballet.FixtureSource(fixture),
                datetime.fromisoformat("2026-08-02T14:20:00+08:00"),
                "2026-08-02T14:20:00+08:00",
            )
        self.assertEqual(snapshot["displayMode"], "sunday_plus_next_week")
        self.assertEqual(snapshot["weekStart"], "2026-08-02")
        self.assertEqual(snapshot["weekEnd"], "2026-08-09")
        self.assertEqual(len(snapshot["days"]), 8)

    def test_timetable_booking_snapshot_only_highlights_owner_states(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            write_fixture(fixture)
            snapshot = ballet.build_timetable_snapshot(
                ballet.FixtureSource(fixture),
                datetime.fromisoformat("2026-07-28T10:00:00+08:00"),
                "2026-07-28T10:00:00+08:00",
                [
                    {
                        "date": "2026-07-28",
                        "startTime": "19:45",
                        "endTime": "21:15",
                        "courseName": "芭蕾L1-入门",
                        "bookingStatus": "waitlist",
                    }
                ],
            )
        course = snapshot["days"][1]["records"][0]
        self.assertEqual(course["availability"], "waitlist")

    def test_membership_forecast_is_isolated_per_card_and_hides_short_samples(self):
        membership = {
            "dataAsOf": "2026-07-27T00:17:00+08:00",
            "cards": [
                {
                    "name": "新卡",
                    "validFrom": "2026-07-26",
                    "validThrough": "2027-01-23",
                    "remainingClasses": 39,
                    "totalClasses": 40,
                    "usedClasses": 1,
                },
                {
                    "name": "旧卡",
                    "validFrom": "2026-06-01",
                    "validThrough": "2026-11-30",
                    "remainingClasses": 32,
                    "totalClasses": 40,
                    "usedClasses": 8,
                },
            ],
        }
        cards = ballet.build_membership_view(membership, NOW)["cards"]
        new_card, mature_card = cards

        self.assertEqual(new_card["pace"]["validityDays"], 182)
        self.assertEqual(new_card["pace"]["openDayNumber"], 2)
        self.assertFalse(new_card["pace"]["sampleSufficient"])
        self.assertIsNone(new_card["pace"]["observedClassesPerWeek"])
        self.assertIsNone(new_card["pace"]["observedCanFinish"])
        self.assertEqual(new_card["pace"]["recommendedWholeClassesPerWeek"], 2)
        self.assertEqual(new_card["pace"]["plannedFinishDate"], "2026-12-10")
        self.assertEqual(new_card["pace"]["oneClassPerWeekProjectedRemaining"], 13)

        self.assertTrue(mature_card["pace"]["sampleSufficient"])
        self.assertEqual(mature_card["pace"]["observedClassesPerWeek"], 1.0)
        self.assertEqual(mature_card["pace"]["openDayNumber"], 57)

        day_one = ballet.build_membership_view(
            {"cards": [membership["cards"][0]]},
            datetime.fromisoformat("2026-07-26T00:17:00+08:00"),
        )["cards"][0]
        self.assertEqual(day_one["pace"]["openDayNumber"], 1)
        self.assertFalse(day_one["pace"]["sampleSufficient"])

        late_card = ballet.build_membership_view(
            {"cards": [membership["cards"][0]]},
            datetime.fromisoformat("2027-01-22T00:17:00+08:00"),
        )["cards"][0]
        self.assertEqual(late_card["pace"]["openDayNumber"], 181)
        self.assertTrue(late_card["pace"]["sampleSufficient"])
        self.assertEqual(late_card["pace"]["remainingDays"], 2)

    def test_fixture_full_sync_is_idempotent_and_public_data_is_redacted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixtures"
            state_dir = root / "private"
            output = root / "public" / "ballet.json"
            write_fixture(fixture)
            paths = ballet.build_paths(state_dir, output)

            first = ballet.synchronize(
                paths,
                ballet.FixtureSource(fixture),
                "full",
                NOW,
            )
            self.assertEqual(first.exit_code, 0)
            self.assertEqual(first.source_records, 2)
            self.assertEqual(first.merged_records, 2)
            model = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(model["summary"]["classes"], 2)
            self.assertEqual(model["summary"]["minutes"], 150)
            self.assertEqual(model["summary"]["hours"], 2.5)
            soft_open = next(
                item
                for item in model["summary"]["byCourseType"]
                if item["key"] == "soft_open"
            )
            self.assertEqual(soft_open["classes"], 1)
            self.assertEqual(soft_open["minutes"], 60)
            self.assertEqual(model["records"][0]["level"], "L1.5")
            self.assertEqual(
                model["upcoming"]["records"][0]["bookingStatus"], "booked"
            )
            self.assertEqual(
                model["upcoming"]["records"][0]["cancelDeadlineAt"],
                "2026-08-02T06:30+08:00",
            )
            self.assertEqual(model["week"]["bookedClasses"], 1)
            self.assertEqual(model["week"]["expectedClassesMin"], 1)
            self.assertEqual(model["timetable"]["displayMode"], "current_week")
            self.assertEqual(model["timetable"]["weekStart"], "2026-07-27")
            self.assertEqual(model["timetable"]["weekEnd"], "2026-08-02")
            self.assertEqual(len(model["timetable"]["days"]), 7)
            card = model["membership"]["cards"][0]
            self.assertEqual(card["remainingClasses"], 39)
            self.assertEqual(card["pace"]["openDayNumber"], 2)
            self.assertFalse(card["pace"]["sampleSufficient"])
            self.assertIsNone(card["pace"]["observedClassesPerWeek"])
            self.assertGreater(card["pace"]["requiredClassesPerWeek"], 0)
            self.assertTrue(all("id" not in record for record in model["records"]))
            self.assertTrue(
                all("id" not in record for record in model["upcoming"]["records"])
            )
            serialized = output.read_text(encoding="utf-8")
            self.assertNotIn("10001", serialized)
            self.assertNotIn("10002", serialized)
            self.assertNotIn("10003", serialized)
            self.assertNotIn("90001", serialized)
            self.assertNotIn("PHPSESSID", serialized)
            self.assertEqual(
                json.loads(output.with_suffix(".js").read_text(encoding="utf-8").split(" = ", 1)[1][:-2]),
                model,
            )

            second = ballet.synchronize(
                paths,
                ballet.FixtureSource(fixture),
                "rolling",
                datetime.fromisoformat("2026-07-28T00:17:00+08:00"),
            )
            self.assertEqual(second.exit_code, 0)
            self.assertEqual(second.changed_records, 0)
            model_again = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(model_again["summary"], model["summary"])
            self.assertEqual(len(model_again["records"]), 2)
            ledger = json.loads(paths.ledger.read_text(encoding="utf-8"))
            self.assertTrue(
                all(
                    "attendanceRecordId" in record["source"]
                    for record in ledger["records"]
                )
            )
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(paths.ledger.stat().st_mode), 0o600)

    def test_auth_failure_keeps_last_good_data_and_exposes_safe_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixtures"
            paths = ballet.build_paths(root / "private", root / "public" / "ballet.json")
            write_fixture(fixture)
            ok = ballet.synchronize(
                paths, ballet.FixtureSource(fixture), "full", NOW
            )
            self.assertEqual(ok.exit_code, 0)
            old_ledger = paths.ledger.read_bytes()

            failed = ballet.synchronize(
                paths,
                AuthFailureSource(),
                "rolling",
                datetime.fromisoformat("2026-07-28T00:17:00+08:00"),
            )
            self.assertEqual(failed.exit_code, 2)
            self.assertEqual(failed.status, "auth_required")
            self.assertEqual(paths.ledger.read_bytes(), old_ledger)
            model = json.loads(paths.output.read_text(encoding="utf-8"))
            self.assertEqual(model["summary"]["classes"], 2)
            self.assertEqual(model["sync"]["lastAttemptStatus"], "auth_required")
            self.assertEqual(model["authHealth"]["status"], "needs_login")
            self.assertIn("重新登录", model["sync"]["errorMessage"])
            self.assertNotIn(SESSION, paths.output.read_text(encoding="utf-8"))

    def test_two_successful_full_misses_tombstone_instead_of_deleting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixtures"
            paths = ballet.build_paths(root / "private", root / "public" / "ballet.json")
            write_fixture(fixture)
            ballet.synchronize(paths, ballet.FixtureSource(fixture), "full", NOW)

            (fixture / "attendance.html").write_text(
                index_html(
                    "上课记录",
                    [("10001", "芭蕾L1.5", "2026-07-26", "")],
                ),
                encoding="utf-8",
            )
            ballet.synchronize(
                paths,
                ballet.FixtureSource(fixture),
                "full",
                datetime.fromisoformat("2026-08-01T00:47:00+08:00"),
            )
            first_model = json.loads(paths.output.read_text(encoding="utf-8"))
            self.assertEqual(first_model["summary"]["classes"], 2)

            ballet.synchronize(
                paths,
                ballet.FixtureSource(fixture),
                "full",
                datetime.fromisoformat("2026-09-01T00:47:00+08:00"),
            )
            second_model = json.loads(paths.output.read_text(encoding="utf-8"))
            self.assertEqual(second_model["summary"]["classes"], 1)
            ledger = json.loads(paths.ledger.read_text(encoding="utf-8"))
            tombstones = [
                item for item in ledger["records"] if item["recordState"] == "tombstone"
            ]
            self.assertEqual(len(tombstones), 1)

    def test_manual_attendance_is_public_and_survives_full_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixtures"
            paths = ballet.build_paths(root / "private", root / "public" / "ballet.json")
            write_fixture(fixture)
            ballet.synchronize(paths, ballet.FixtureSource(fixture), "full", NOW)

            ledger = json.loads(paths.ledger.read_text(encoding="utf-8"))
            manual = ballet.normalize_manual_attendance(
                {
                    "courseName": "软开课",
                    "date": "2026-07-25",
                    "startTime": "11:30",
                    "endTime": "12:30",
                    "teacher": "李俊",
                },
                "2026-07-27T12:30:00+08:00",
            )
            ledger["records"].append(manual)
            ledger["contentFingerprint"] = ballet.content_fingerprint(ledger["records"])
            ballet.validate_ledger(ledger)
            ballet.atomic_write_json(paths.ledger, ledger, mode=0o600)

            ballet.synchronize(
                paths,
                ballet.FixtureSource(fixture),
                "full",
                datetime.fromisoformat("2026-08-01T00:47:00+08:00"),
            )
            model = json.loads(paths.output.read_text(encoding="utf-8"))
            manual_public = next(
                item for item in model["records"] if item["recordOrigin"] == "manual"
            )
            self.assertEqual(manual_public["courseName"], "软开课")
            self.assertEqual(manual_public["durationMinutes"], 60)
            self.assertEqual(model["summary"]["classes"], 3)
            self.assertEqual(model["summary"]["minutes"], 210)
            stored = json.loads(paths.ledger.read_text(encoding="utf-8"))
            manual_private = next(
                item for item in stored["records"] if item["keySource"] == "manual"
            )
            self.assertEqual(manual_private["recordState"], "active")

    def test_fixture_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixtures"
            state_dir = root / "does-not-exist"
            output = root / "public" / "ballet.json"
            write_fixture(fixture)
            result = ballet.synchronize(
                ballet.build_paths(state_dir, output),
                ballet.FixtureSource(fixture),
                "full",
                NOW,
                dry_run=True,
            )
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(state_dir.exists())
            self.assertFalse(output.exists())

    def test_cli_dry_run_never_requires_credentials(self):
        environment = os.environ.copy()
        environment.pop("WENDA_CREDENTIAL_FILE", None)
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).with_name("sync_ballet.py")),
                "--dry-run",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            env=environment,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "configuration_valid")
        self.assertNotIn(SESSION, result.stdout + result.stderr)

    def test_cli_auth_block_does_not_read_credentials_or_use_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_dir = root / "state"
            state_dir.mkdir()
            state = ballet.empty_sync_state()
            state.update(
                {
                    "lastAttemptStatus": "auth_required",
                    "credentialVersion": "generation-1",
                }
            )
            (state_dir / "sync-state.json").write_text(
                json.dumps(state),
                encoding="utf-8",
            )
            version_path = root / "credential-version"
            version_path.write_text("generation-1\n", encoding="utf-8")
            if os.name != "nt":
                version_path.chmod(0o400)

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(Path(__file__).with_name("sync_ballet.py")),
                    "--state-dir",
                    str(state_dir),
                    "--output",
                    str(root / "public" / "ballet.json"),
                    "--credential-file",
                    str(root / "must-not-be-read.json"),
                    "--credential-version-file",
                    str(version_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "auth_blocked")
            self.assertFalse((root / "public").exists())


if __name__ == "__main__":
    unittest.main()
