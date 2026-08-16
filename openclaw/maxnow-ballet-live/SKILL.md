---
name: maxnow-ballet-live
description: Query the owner's current ballet timetable, bookings, attendance, course availability, membership balance, explicit bookings, and Sunday automatic-booking plan or results through the MaxNow server. Use whenever the owner asks for ballet classes, schedules, booking, automatic booking, grabbing classes, waitlists, attendance, teachers, course cards, or remaining-class data. Never answer course-data requests from MaxNow dashboard caches.
---

# MaxNow Ballet Live

Always query Wenda live through the MaxNow server. Never read `dash/data/ballet.json`, `ballet.js`, browser storage, private ledgers, snapshots, or prior chat results as the answer or as a booking input.

## Workflow

1. Resolve relative dates in `Asia/Shanghai` and convert them to ISO dates.
2. Select the smallest live scope that answers the question:
   - `timetable`: classes and live availability for one date or a date range.
   - `bookings`: current booked and waitlisted classes, positions, and cancellation deadlines.
   - `attendance`: live attendance records; pass a date range when the request supplies one.
   - `membership`: course-card validity and remaining classes.
3. From outside the server, run:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 ubuntu@43.160.240.244 \
  "cd /var/www/maxnow-dashboard && scripts/run_ballet_live_query.sh <scope> [--from-date YYYY-MM-DD] [--through-date YYYY-MM-DD]"
```

When already running on the MaxNow server, omit SSH and run the command after changing to `/var/www/maxnow-dashboard`.

Examples:

```bash
scripts/run_ballet_live_query.sh timetable --from-date 2026-07-28 --through-date 2026-08-03
scripts/run_ballet_live_query.sh bookings
scripts/run_ballet_live_query.sh attendance --from-date 2026-07-01 --through-date 2026-07-31
scripts/run_ballet_live_query.sh membership
```

4. Require a successful JSON response with all of:
   - `"source":"wenda-live"`
   - `"status":"success"`
   - `"live":true`
   - a current `fetchedAt`
5. Answer from `data` and state the live query time. If the command fails, report the safe error and say no live data was returned. Do not fall back to cached data.
6. For `attendance` only, the shared normalization rule returns `李俊` when Wenda leaves the teacher field empty, except that the owner-confirmed 2026-08-07 19:45–21:15 ballet L1 record returns `张瀚泽`. Do not apply defaults or history corrections to timetable, booking, or waitlist records.

## Booking Workflow

Only book when the owner explicitly asks to book one or more exact classes. An exact class requires date, start time, end time, course name, teacher, and venue. Do not infer a different class when any field does not match.

1. Build this JSON on stdin:

```json
{
  "courses": [
    {
      "date": "2026-07-30",
      "startTime": "20:15",
      "endTime": "21:15",
      "courseName": "肌肉素质",
      "teacher": "戴俊瑶",
      "venue": "小教室"
    }
  ],
  "confirm": false
}
```

2. Run a live preflight through the repository runner:

```bash
scripts/run_ballet_booking.sh dry-run
```

The preflight may use Wenda's fixed read-only POST checks for eligible cards and booking rules. It must never call `do_addbook`. Require `status=success`, `live=true`, every target record `status=ready` or `already_booked`, and `mutationAttempts=0`.

3. If the owner has explicitly requested those exact classes in the current request, change only `confirm` to `true` and run:

```bash
scripts/run_ballet_booking.sh execute
```

The runner performs a unified live preflight, then books courses sequentially. Before each mutation it rechecks availability, eligible card, and booking rules. It sends at most one `do_addbook` request per course, immediately verifies the result from live bookings, returns one result per course, and stops after an ambiguous or authentication failure. Never retry an ambiguous mutation.

For multiple exact classes without an owner-specified order, sort them by the permanent weekday priority `周六 > 周日 > 周五 > 其他日期`, then keep the original order within the same weekday.

4. Report only the safe per-course result. A course is booked only when its result is `status=booked` and live verification returns `bookingStatus=booked`. If the command returns `card_selection_required`, ask the owner which eligible card to use; never choose a card silently.

## Sunday Automatic Booking

The enabled production fast path runs entirely on the MaxNow server. It arms at Sunday 14:19:35 Beijing time, warms the live session, waits until 14:20:00, and submits configured targets sequentially. It does not invoke Codex, this Skill, or SSH on the timing-critical path.

After release, the fast path reads Monday through Saturday timetable pages and dynamically discovers every matching occurrence. Each discovered occurrence is an independent failure domain. Match exactly one live course by date, exact discovered course name, course type/level, start/end time, and selected venue. Teacher is display-only and must not affect matching or the occurrence idempotency key, so a substitute teacher does not block a configured rule. Transient pre-mutation failures and an explicit `NOTOPEN` response may be retried three times with short bounded backoff. A course-level failure or ambiguous mutation must not block later targets. Never retry an ambiguous mutation because Wenda may already have accepted it; include it in the final unified live-bookings verification instead. Stop later targets only for a global safety failure such as expired authentication, invalid configuration, or a changed page/endpoint contract.

For these configured recurring targets only, `allowWaitlist=true` authorizes the same exact-course fast path to join the waitlist when live availability is `queue_available`. If availability is `available`, book normally. If it is already `booked` or `waitlist`, do not submit again. Final verification must preserve Wenda's actual `bookingStatus` (`booked` or `waitlist`) and a safe positive `waitlistPosition` when present. This authorization does not extend to conversational bookings or any unconfigured class.

Current recurring rules are:

- Monday through Saturday, all day: every standard ballet L1 occurrence, any teacher.
- Monday through Saturday, all day: only a course whose normalized name is exactly `软开`, any teacher.
- Sunday courses are excluded. `软开专项`, `软开-胯`, and any other merely soft-open-classified near match are excluded.
- For the same occurrence, prefer `大教室`; use `小教室` only when the large-room tier has no match. The selected tier must contain exactly one course.

For the Sunday fast path, process Saturday first, then Monday through Friday; within a day sort by start time, with `软开` before ballet L1 only when times tie. Timetable GETs may run with at most three workers and share a page by date; card/rules preflight may run with at most two workers and expires after eight seconds. Actual booking or waitlist mutations must remain strictly serial in that priority order. Final booking-detail verification may use at most three read-only workers.

To query the automation plan and safe result ledger, run:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 ubuntu@43.160.240.244 \
  "cd /var/www/maxnow-dashboard && scripts/run_ballet_booking_fast.sh status"
```

The automation status ledger is allowed only for plan, last/next run, configured targets, and aggregate result questions. It is not a source for course availability. For any timetable or availability question, use the live query workflow above.

Do not manually start the production service or run `book_ballet_fast.py execute` from a conversation. Changes to automatic targets require a reviewed configuration change, tests, deployment, and a refreshed safe status snapshot.

## Timetable Answer Contract

- Treat generic questions such as “有什么课程” or “有什么可以约的课” as requests for every returned course type. Do not filter `courseType` by default; include ballet, conditioning, soft-open, technique, and any future types returned by the live source.
- Apply a course-type filter only when the owner explicitly says “只看”, “仅看”, “只想看”, or otherwise clearly limits the answer to named course types. Do not interpret the umbrella phrase “芭蕾课程” by itself as `courseType=ballet`.
- For availability questions, list future records with `availability=available` as the primary result. State the number of `queue_available` records separately, but do not mix waitlist-only rows into the directly bookable list unless the owner asks to see them.
- Group rows by date using `**周X M/D**`. Format every directly bookable row as `- HH:MM–HH:MM 课程名｜老师｜教室｜余N`, where `余N` is `capacity - bookedCount`.
- Include both start and end time on every course row. End with the live query time and state that no cache was used.

## Safety Boundary

- Use only the repository runners. They create hardened transient systemd units, decrypt the host-bound credential into the unit credential directory, and remove that runtime directory when done.
- Allow only the four scopes and ISO date arguments. A timetable request may span at most 14 days.
- Never print, copy, inspect, hash, summarize, or ask the owner for PHPSESSID. Never read `/etc/credstore.encrypted` directly.
- For ordinary queries, never use POST. For an explicitly confirmed booking, allow only the fixed card-eligibility check, booking-rules check, and one `do_addbook` request per exact course through `run_ballet_booking.sh`.
- Never use cancellation, transfer, payment, login, or arbitrary POST endpoints. Waitlist mutation is forbidden for ordinary queries and conversational booking; it is allowed only inside the enabled Sunday fast path for an exact configured target with `allowWaitlist=true`.
- Never expose source record IDs, member identifiers, raw HTML, response bodies, Cookie headers, credential paths, unit names, or internal logs.
- Treat `auth_required`, `source_changed`, `parse_error`, `unknown_result`, and ambiguous responses as fail-closed. If any mutation was attempted and the result is ambiguous, report that verification is required; never claim failure or retry.
- For the Sunday automatic fast path only, fail-closed is scoped per course: an ambiguous mutation is never retried, but later configured courses still proceed and all ambiguous/successful submissions are verified together. Authentication, configuration, and source-contract failures remain global stops.
