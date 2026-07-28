---
name: maxnow-ballet-live
description: Query the owner's current ballet timetable, upcoming bookings and waitlist positions, attendance records, teachers, course availability, or membership balance from the live Wenda source through the MaxNow server. Use whenever the owner asks for ballet class, schedule, booking, waitlist, attendance, teacher, course-card, or remaining-class data. Never answer these requests from MaxNow dashboard caches.
---

# MaxNow Ballet Live

Always query Wenda live through the MaxNow server. Never read `dash/data/ballet.json`, `ballet.js`, browser storage, private ledgers, snapshots, or prior chat results as the answer.

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

## Timetable Answer Contract

- Treat generic questions such as “有什么课程” or “有什么可以约的课” as requests for every returned course type. Do not filter `courseType` by default; include ballet, conditioning, soft-open, technique, and any future types returned by the live source.
- Apply a course-type filter only when the owner explicitly says “只看”, “仅看”, “只想看”, or otherwise clearly limits the answer to named course types. Do not interpret the umbrella phrase “芭蕾课程” by itself as `courseType=ballet`.
- For availability questions, list future records with `availability=available` as the primary result. State the number of `queue_available` records separately, but do not mix waitlist-only rows into the directly bookable list unless the owner asks to see them.
- Group rows by date using `**周X M/D**`. Format every directly bookable row as `- HH:MM–HH:MM 课程名｜老师｜教室｜余N`, where `余N` is `capacity - bookedCount`.
- Include both start and end time on every course row. End with the live query time and state that no cache was used.

## Safety Boundary

- Use only the repository runner. It creates a read-only transient systemd unit, decrypts the host-bound credential into the unit credential directory, and removes that runtime directory when done.
- Allow only the four scopes and ISO date arguments. A timetable request may span at most 14 days.
- Never print, copy, inspect, hash, summarize, or ask the owner for PHPSESSID. Never read `/etc/credstore.encrypted` directly.
- Never use POST or any booking, cancellation, transfer, payment, or login endpoint.
- Never expose source record IDs, member identifiers, raw HTML, response bodies, Cookie headers, credential paths, unit names, or internal logs.
- Treat `auth_required`, `source_changed`, `parse_error`, and ambiguous responses as fail-closed.
