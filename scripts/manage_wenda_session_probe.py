"""Switch the server's read-only probe when the production credential is replaced."""

import argparse
import grp
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import time


CONFIG = Path("/etc/maxnow-ballet/session-experiment.json")
VERSION = CONFIG.with_name("credential-version")
SOURCE_DIRECTORY = Path("/var/lib/maxnow-ballet-session-source")
PRIVATE_DIRECTORY = Path("/var/lib/private")
PROBE_UNIT = "maxnow-wenda-session-probe@"
LEGACY_UNIT = "maxnow-wenda-session-lifetime-20261114-v8.service"
VERSION_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")


def systemctl(*args):
    subprocess.run(["/usr/bin/systemctl", *args], check=True, timeout=30)


def current_phase(config):
    return next(phase for phase in config["phases"] if phase["key"] == config["currentPhase"])


def read_log(path):
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as log:
        info = os.fstat(log.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Invalid probe log file")
        contents = log.read()
    # The active probe can append while the exporter reads.
    return contents[: contents.rfind(b"\n") + 1]


def publish(path, contents):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        try:
            temporary.write(contents)
            temporary.flush()
            os.fchown(temporary.fileno(), 0, grp.getgrnam("maxnow-ballet-status").gr_gid)
            os.fchmod(temporary.fileno(), 0o640)
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)


def wait_for_start(log):
    for _ in range(50):
        try:
            lines = read_log(log).splitlines()
        except FileNotFoundError:
            lines = []
        if lines:
            start = json.loads(lines[0])
            if start["event"] != "start" or start["interval_seconds"] != 1200:
                raise ValueError("Invalid start record for Wenda probe")
            return start["timestamp"]
        time.sleep(0.2)
    raise RuntimeError("Wenda probe did not start")


def read_version():
    version = VERSION.read_text(encoding="ascii").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("Invalid production credential version")
    return version


def probe_log(version):
    return PRIVATE_DIRECTORY / f"maxnow-wenda-session-probe-{version}" / "probe.jsonl"


def handoff(config):
    previous = current_phase(config)["unit"] if config else None
    while True:
        version = read_version()
        unit = f"{PROBE_UNIT}{version}.service"
        if previous == unit:
            return
        log = probe_log(version)
        if not log.exists():
            systemctl("start", unit)
        started = wait_for_start(log)
        if read_version() != version:
            systemctl("stop", unit)
            continue
        phase = {
            "key": version,
            "unit": unit,
            "log": str(SOURCE_DIRECTORY / f"{version}.jsonl"),
            "intervalSeconds": 1200,
            "handoffValidationSamples": 0,
        }
        config = {
            "schemaVersion": 1,
            "experimentStartedAt": started,
            "scheduledEndAt": None,
            "currentPhase": version,
            "phases": [phase],
        }
        export(config)
        publish(CONFIG, json.dumps(config).encode())
        if previous and (previous == LEGACY_UNIT or previous.startswith(PROBE_UNIT)):
            systemctl("stop", previous)
        previous = unit


def export(config):
    phase = current_phase(config)
    if phase["unit"] == LEGACY_UNIT:
        log = PRIVATE_DIRECTORY / "maxnow-wenda-session-v8/server-lifetime-20261114-continuous-20min.jsonl"
        destination = SOURCE_DIRECTORY / "v8-continuous-20m.jsonl"
    else:
        version = phase["key"]
        if not VERSION_PATTERN.fullmatch(version) or phase["unit"] != f"{PROBE_UNIT}{version}.service":
            raise ValueError("Invalid Wenda probe generation")
        log = probe_log(version)
        destination = SOURCE_DIRECTORY / f"{version}.jsonl"
    publish(destination, read_log(log))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("handoff", "export"))
    action = parser.parse_args().action
    config = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else None
    if action == "handoff":
        handoff(config)
    else:
        export(config)


if __name__ == "__main__":
    main()
