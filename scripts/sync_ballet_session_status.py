#!/usr/bin/env python3
"""Publish a strictly redacted view of the Wenda session-lifetime experiment.

The publisher reads only a root-owned local configuration and the JSONL files
listed by that configuration. It has no network client and never copies source
records into the public read model.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TIMEZONE_NAME = "Asia/Shanghai"
LOCAL_TIMEZONE = timezone(timedelta(hours=8), name=TIMEZONE_NAME)
PUBLIC_SCHEMA_VERSION = 1
COMPLETE_EARLY_TOLERANCE_SECONDS = 120
FINAL_REQUEST_SAFETY_SECONDS = 5
CONFIG_KEYS = {
    "schemaVersion",
    "experimentStartedAt",
    "scheduledEndAt",
    "currentPhase",
    "phases",
}
PHASE_KEYS = {
    "key",
    "unit",
    "log",
    "intervalSeconds",
    "handoffValidationSamples",
}
PUBLIC_KEYS = {
    "schemaVersion",
    "timezone",
    "updatedAt",
    "status",
    "experimentStartedAt",
    "phaseStartedAt",
    "lastProbeAt",
    "lastAuthenticatedAt",
    "nextProbeAt",
    "scheduledEndAt",
    "refreshIntervalMinutes",
    "verifiedAliveSeconds",
    "phaseSamples",
    "totalSamples",
    "sessionChangedObserved",
    "setCookieObserved",
    "lastResult",
    "lastError",
}
SERVICE_STATES = {
    "active",
    "activating",
    "inactive",
    "deactivating",
    "failed",
    "unknown",
}
LOGIN_STATES = {
    "authenticated",
    "expired",
    "network_error",
    "redirect",
    "unknown",
}
TERMINAL_EVENTS = {
    "complete",
    "stopped_identity_expired",
    "stopped_consecutive_unknown",
}
UNIT_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]+\.service$")


class StatusPublishError(ValueError):
    """A safe configuration or source-data error."""


@dataclass(frozen=True)
class PhaseConfig:
    key: str
    unit: str
    log: Path
    interval_seconds: int
    handoff_validation_samples: int


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_started_at: datetime
    scheduled_end_at: datetime
    current_phase: str
    phases: tuple[PhaseConfig, ...]

    @property
    def phase(self) -> PhaseConfig:
        return next(item for item in self.phases if item.key == self.current_phase)


@dataclass
class ParsedPhase:
    started_at: datetime | None
    interval_seconds: int | None
    samples: list[dict[str, Any]]
    terminal_event: str | None
    terminal_at: datetime | None
    invalid_records: int


def format_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(LOCAL_TIMEZONE).isoformat(timespec="seconds")


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise StatusPublishError(f"{field} must be a timezone-aware timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError as error:
        raise StatusPublishError(
            f"{field} must be a timezone-aware timestamp"
        ) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise StatusPublishError(f"{field} must be a timezone-aware timestamp")
    return parsed


def assert_restricted_config(path: Path) -> None:
    """Require a regular, single-link, root-owned restricted file on POSIX."""

    if os.name == "nt":
        return
    metadata = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise StatusPublishError("config must be a regular single-link file")
    mode = stat.S_IMODE(metadata.st_mode)
    if metadata.st_uid != 0 or mode & 0o027:
        raise StatusPublishError(
            "config must be root-owned, group-read-only, and closed to others"
        )


def validate_config(payload: Any) -> ExperimentConfig:
    if not isinstance(payload, dict) or set(payload) != CONFIG_KEYS:
        raise StatusPublishError("config contains missing or unsupported fields")
    if payload.get("schemaVersion") != 1:
        raise StatusPublishError("config schemaVersion must be 1")

    experiment_started_at = parse_timestamp(
        payload.get("experimentStartedAt"), "experimentStartedAt"
    )
    scheduled_end_at = parse_timestamp(
        payload.get("scheduledEndAt"), "scheduledEndAt"
    )
    if scheduled_end_at <= experiment_started_at:
        raise StatusPublishError("scheduledEndAt must follow experimentStartedAt")

    current_phase = payload.get("currentPhase")
    if not isinstance(current_phase, str) or not current_phase.strip():
        raise StatusPublishError("currentPhase is required")

    raw_phases = payload.get("phases")
    if not isinstance(raw_phases, list) or not raw_phases:
        raise StatusPublishError("phases must be a non-empty list")

    phases: list[PhaseConfig] = []
    keys: set[str] = set()
    for raw_phase in raw_phases:
        if not isinstance(raw_phase, dict) or set(raw_phase) != PHASE_KEYS:
            raise StatusPublishError(
                "phase contains missing or unsupported fields"
            )
        key = raw_phase.get("key")
        unit = raw_phase.get("unit")
        log = raw_phase.get("log")
        interval_seconds = raw_phase.get("intervalSeconds")
        validation_samples = raw_phase.get("handoffValidationSamples")
        if not isinstance(key, str) or not key.strip() or key in keys:
            raise StatusPublishError("phase keys must be unique non-empty strings")
        if not isinstance(unit, str) or not UNIT_PATTERN.fullmatch(unit):
            raise StatusPublishError("phase unit must be a safe systemd service name")
        if not isinstance(log, str) or not Path(log).is_absolute():
            raise StatusPublishError("phase log must be an absolute path")
        if (
            not isinstance(interval_seconds, int)
            or isinstance(interval_seconds, bool)
            or interval_seconds < 60
            or interval_seconds > 86_400
            or interval_seconds % 60
        ):
            raise StatusPublishError(
                "phase intervalSeconds must be whole minutes between 60 and 86400"
            )
        if (
            not isinstance(validation_samples, int)
            or isinstance(validation_samples, bool)
            or validation_samples < 0
            or validation_samples > 100
        ):
            raise StatusPublishError(
                "phase handoffValidationSamples must be between 0 and 100"
            )
        keys.add(key)
        phases.append(
            PhaseConfig(
                key=key,
                unit=unit,
                log=Path(log),
                interval_seconds=interval_seconds,
                handoff_validation_samples=validation_samples,
            )
        )
    if current_phase not in keys:
        raise StatusPublishError("currentPhase does not match a configured phase")
    return ExperimentConfig(
        experiment_started_at=experiment_started_at,
        scheduled_end_at=scheduled_end_at,
        current_phase=current_phase,
        phases=tuple(phases),
    )


def load_config(path: Path, *, enforce_permissions: bool = True) -> ExperimentConfig:
    if enforce_permissions:
        assert_restricted_config(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise StatusPublishError("config could not be read as JSON") from error
    return validate_config(payload)


def safe_sample(record: dict[str, Any]) -> dict[str, Any] | None:
    sample = record.get("sample")
    if not isinstance(sample, int) or isinstance(sample, bool):
        return None
    if "http_status" not in record:
        return None
    try:
        timestamp = parse_timestamp(record.get("timestamp"), "sample timestamp")
    except StatusPublishError:
        return None

    raw_status = record.get("http_status")
    http_status = (
        raw_status
        if isinstance(raw_status, int)
        and not isinstance(raw_status, bool)
        and 100 <= raw_status <= 599
        else None
    )
    raw_login_state = record.get("login_state")
    if not isinstance(raw_login_state, str) or raw_login_state not in LOGIN_STATES:
        return None
    login_state = raw_login_state
    raw_attempts = record.get("attempts")
    attempts = (
        raw_attempts
        if isinstance(raw_attempts, int)
        and not isinstance(raw_attempts, bool)
        and 1 <= raw_attempts <= 6
        else None
    )
    return {
        "sample": sample,
        "timestamp": timestamp,
        "http_status": http_status,
        "login_state": login_state,
        "attempts": attempts,
        "network_error": bool(record.get("network_error")),
        "session_changed": bool(record.get("session_changed")),
        "set_cookie": bool(record.get("set_cookie")),
    }


def parse_phase_log(path: Path) -> ParsedPhase:
    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ParsedPhase(None, None, [], None, None, 1)

    started_at: datetime | None = None
    interval_seconds: int | None = None
    samples: list[dict[str, Any]] = []
    terminal_event: str | None = None
    terminal_at: datetime | None = None
    invalid_records = 0
    for raw_line in raw_lines:
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            invalid_records += 1
            continue
        if not isinstance(record, dict):
            invalid_records += 1
            continue
        event = record.get("event")
        if event == "start":
            try:
                candidate = parse_timestamp(
                    record.get("timestamp"), "phase start timestamp"
                )
            except StatusPublishError:
                invalid_records += 1
            else:
                if started_at is None:
                    started_at = candidate
                    raw_interval = record.get("interval_seconds")
                    if (
                        isinstance(raw_interval, int)
                        and not isinstance(raw_interval, bool)
                        and 60 <= raw_interval <= 86_400
                        and raw_interval % 60 == 0
                    ):
                        interval_seconds = raw_interval
                    else:
                        invalid_records += 1
                elif candidate != started_at:
                    invalid_records += 1
        if isinstance(event, str) and event in TERMINAL_EVENTS:
            try:
                candidate_terminal_at = parse_timestamp(
                    record.get("timestamp"), "terminal timestamp"
                )
            except StatusPublishError:
                invalid_records += 1
            else:
                if terminal_event is not None:
                    invalid_records += 1
                terminal_event = event
                terminal_at = candidate_terminal_at
        sample = safe_sample(record)
        if sample is not None:
            samples.append(sample)
        elif isinstance(record.get("sample"), int) and "http_status" in record:
            invalid_records += 1
    samples.sort(key=lambda item: (item["timestamp"], item["sample"]))
    return ParsedPhase(
        started_at,
        interval_seconds,
        samples,
        terminal_event,
        terminal_at,
        invalid_records,
    )


def inspect_service_state(unit: str) -> str:
    try:
        result = subprocess.run(
            [
                "/usr/bin/systemctl",
                "show",
                unit,
                "--property=ActiveState",
                "--value",
                "--no-pager",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
            check=False,
            env={
                "PATH": "/usr/bin:/bin",
                "LANG": "C",
                "LC_ALL": "C",
            },
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    state = result.stdout.strip()
    return state if result.returncode == 0 and state in SERVICE_STATES else "unknown"


def controlled_error(
    status: str,
    *,
    terminal_event: str | None,
    invalid_records: int,
    interval_mismatch: bool,
    last_sample: dict[str, Any] | None,
) -> dict[str, str] | None:
    if status in {"running", "complete"}:
        return None
    if status == "auth_required":
        return {
            "code": "identity_expired",
            "message": "PHPSESSID 已失效，请在电脑微信重新登录并刷新服务器凭据。",
        }
    if status == "delayed":
        return {
            "code": "probe_delayed",
            "message": "只读检查已超过预期时间，当前登录状态待确认。",
        }
    if interval_mismatch:
        return {
            "code": "source_config_mismatch",
            "message": "实验配置与日志中的检查间隔不一致。",
        }
    if invalid_records:
        return {
            "code": "source_log_invalid",
            "message": "实验状态日志暂时无法完整解析。",
        }
    if terminal_event == "complete":
        return {
            "code": "invalid_completion",
            "message": "实验完成标记尚未通过时间与样本完整性校验。",
        }
    if status == "interrupted":
        return {
            "code": "probe_interrupted",
            "message": "自动检查服务已停止，当前登录状态待确认。",
        }
    if terminal_event == "stopped_consecutive_unknown":
        return {
            "code": "probe_inconclusive",
            "message": "连续检查无法确认登录状态，实验已安全停止。",
        }
    if last_sample and (
        last_sample["network_error"]
        or last_sample["login_state"] == "network_error"
    ):
        return {
            "code": "network_error",
            "message": "最近一次只读检查遇到网络异常。",
        }
    if last_sample and last_sample["login_state"] == "redirect":
        return {
            "code": "unknown_response",
            "message": "最近一次响应发生跳转，当前登录状态待确认。",
        }
    if (
        last_sample
        and last_sample["http_status"] is not None
        and last_sample["http_status"] != 200
    ):
        return {
            "code": "http_error",
            "message": "最近一次只读检查返回异常 HTTP 状态。",
        }
    if last_sample and last_sample["login_state"] == "unknown":
        return {
            "code": "unknown_response",
            "message": "最近一次响应无法安全判断登录状态。",
        }
    return {
        "code": "status_unknown",
        "message": "暂时无法确认 PHPSESSID 的当前状态。",
    }


def build_public_model(
    config: ExperimentConfig,
    *,
    now: datetime | None = None,
    service_state: str | None = None,
) -> dict[str, Any]:
    current_time = (now or datetime.now(LOCAL_TIMEZONE)).astimezone(
        LOCAL_TIMEZONE
    )
    if service_state is None:
        service_state = inspect_service_state(config.phase.unit)
    if service_state not in SERVICE_STATES:
        service_state = "unknown"

    parsed = {
        phase.key: parse_phase_log(phase.log) for phase in config.phases
    }
    current_log = parsed[config.current_phase]
    all_samples = [
        sample
        for phase in config.phases
        for sample in parsed[phase.key].samples
    ]
    all_samples.sort(key=lambda item: (item["timestamp"], item["sample"]))
    last_sample = all_samples[-1] if all_samples else None
    current_last_sample = (
        current_log.samples[-1] if current_log.samples else None
    )
    authenticated_samples = [
        sample
        for sample in all_samples
        if sample["login_state"] == "authenticated"
    ]
    last_authenticated = (
        authenticated_samples[-1] if authenticated_samples else None
    )

    terminal_event = current_log.terminal_event
    invalid_records = sum(item.invalid_records for item in parsed.values())
    interval_mismatch = any(
        parsed[phase.key].started_at is not None
        and parsed[phase.key].interval_seconds != phase.interval_seconds
        for phase in config.phases
    )
    freshness_seconds = config.phase.interval_seconds * 2 + 5 * 60
    last_probe_age = (
        max(
            0,
            int(
                (
                    current_time - current_last_sample["timestamp"]
                ).total_seconds()
            ),
        )
        if current_last_sample
        else None
    )
    complete_is_valid = False
    if (
        terminal_event == "complete"
        and service_state == "inactive"
        and not invalid_records
        and not interval_mismatch
        and current_log.started_at is not None
        and current_log.terminal_at is not None
        and current_last_sample is not None
        and current_last_sample["login_state"] == "authenticated"
        and current_log.started_at <= config.scheduled_end_at
        and current_log.started_at <= current_log.terminal_at
        and current_log.terminal_at >= current_last_sample["timestamp"]
        and current_log.terminal_at <= current_time + timedelta(minutes=5)
        and current_log.terminal_at
        >= config.scheduled_end_at
        - timedelta(seconds=COMPLETE_EARLY_TOLERANCE_SECONDS)
    ):
        coverage_seconds = max(
            0,
            int(
                (
                    config.scheduled_end_at
                    - timedelta(seconds=FINAL_REQUEST_SAFETY_SECONDS)
                    - current_log.started_at
                ).total_seconds()
            ),
        )
        expected_complete_samples = max(
            config.phase.handoff_validation_samples,
            coverage_seconds // config.phase.interval_seconds + 1,
        )
        complete_is_valid = (
            len(current_log.samples) >= expected_complete_samples
        )

    if terminal_event == "stopped_identity_expired" or (
        current_last_sample
        and current_last_sample["login_state"] == "expired"
    ):
        status = "auth_required"
    elif complete_is_valid:
        status = "complete"
    elif terminal_event == "stopped_consecutive_unknown":
        status = "unknown"
    elif service_state == "active":
        if (
            current_last_sample is None
            or current_log.started_at is None
            or invalid_records
            or interval_mismatch
            or len(current_log.samples)
            < max(1, config.phase.handoff_validation_samples)
        ):
            status = "unknown"
        elif last_probe_age is not None and last_probe_age > freshness_seconds:
            status = "delayed"
        elif current_last_sample["login_state"] == "authenticated":
            status = "running"
        else:
            status = "unknown"
    elif service_state in {"inactive", "failed", "deactivating"}:
        status = "interrupted"
    else:
        status = "unknown"

    next_probe_at: datetime | None = None
    if status == "running" and current_log.started_at is not None:
        next_probe_at = current_log.started_at + timedelta(
            seconds=len(current_log.samples) * config.phase.interval_seconds
        )

    verified_alive_seconds = 0
    if last_authenticated is not None:
        verified_alive_seconds = max(
            0,
            int(
                (
                    last_authenticated["timestamp"]
                    - config.experiment_started_at
                ).total_seconds()
            ),
        )

    last_result = None
    if last_sample is not None:
        last_result = {
            "httpStatus": last_sample["http_status"],
            "loginState": last_sample["login_state"],
            "attempts": last_sample["attempts"],
            "networkError": last_sample["network_error"],
        }

    model = {
        "schemaVersion": PUBLIC_SCHEMA_VERSION,
        "timezone": TIMEZONE_NAME,
        "updatedAt": format_timestamp(current_time),
        "status": status,
        "experimentStartedAt": format_timestamp(config.experiment_started_at),
        "phaseStartedAt": format_timestamp(current_log.started_at),
        "lastProbeAt": (
            format_timestamp(last_sample["timestamp"]) if last_sample else None
        ),
        "lastAuthenticatedAt": (
            format_timestamp(last_authenticated["timestamp"])
            if last_authenticated
            else None
        ),
        "nextProbeAt": format_timestamp(next_probe_at),
        "scheduledEndAt": format_timestamp(config.scheduled_end_at),
        "refreshIntervalMinutes": config.phase.interval_seconds // 60,
        "verifiedAliveSeconds": verified_alive_seconds,
        "phaseSamples": len(current_log.samples),
        "totalSamples": len(all_samples),
        "sessionChangedObserved": any(
            sample["session_changed"] for sample in all_samples
        ),
        "setCookieObserved": any(
            sample["set_cookie"] for sample in all_samples
        ),
        "lastResult": last_result,
        "lastError": controlled_error(
            status,
            terminal_event=terminal_event,
            invalid_records=invalid_records,
            interval_mismatch=interval_mismatch,
            last_sample=current_last_sample,
        ),
    }
    if set(model) != PUBLIC_KEYS:
        raise AssertionError("public model fields drifted from the allowlist")
    return model


def target_metadata(path: Path) -> tuple[int, int | None, int | None]:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return 0o644, None, None
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise StatusPublishError("output must be a regular single-link file")
    return (
        stat.S_IMODE(metadata.st_mode),
        getattr(metadata, "st_uid", None),
        getattr(metadata, "st_gid", None),
    )


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode, owner, group = target_metadata(path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(
            descriptor, "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if os.name == "nt":
            os.chmod(temporary_path, mode)
        else:
            os.chmod(temporary_path, mode, follow_symlinks=False)
        if (
            os.name != "nt"
            and owner is not None
            and group is not None
            and hasattr(os, "chown")
        ):
            os.chown(temporary_path, owner, group, follow_symlinks=False)
        os.replace(temporary_path, path)
        if os.name != "nt":
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def serialize_model(model: dict[str, Any]) -> tuple[str, str]:
    json_content = json.dumps(
        model, ensure_ascii=False, indent=2, sort_keys=False
    ) + "\n"
    wrapper_content = f"window.MAXNOW_BALLET_SESSION_DATA = {json_content.rstrip()};\n"
    return json_content, wrapper_content


def publish(
    config: ExperimentConfig,
    output: Path,
    wrapper: Path,
    *,
    now: datetime | None = None,
    service_state: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    model = build_public_model(
        config, now=now, service_state=service_state
    )
    if not dry_run:
        json_content, wrapper_content = serialize_model(model)
        atomic_write(output, json_content)
        atomic_write(wrapper, wrapper_content)
    return model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a redacted local view of the ballet session probe."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dash/data/ballet-session.json"),
    )
    parser.add_argument(
        "--wrapper",
        type=Path,
        default=Path("dash/data/ballet-session.js"),
    )
    parser.add_argument(
        "--service-state",
        choices=sorted(SERVICE_STATES),
        help="Override systemctl state for controlled tests.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the public model without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        model = publish(
            config,
            args.output,
            args.wrapper,
            service_state=args.service_state,
            dry_run=args.dry_run,
        )
    except (OSError, StatusPublishError) as error:
        message = (
            str(error)
            if isinstance(error, StatusPublishError)
            else "local status file operation failed"
        )
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": type(error).__name__,
                    "message": message,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 1
    print(
        json.dumps(
            {
                "status": "dry_run" if args.dry_run else "published",
                "publicStatus": model["status"],
                "updatedAt": model["updatedAt"],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
