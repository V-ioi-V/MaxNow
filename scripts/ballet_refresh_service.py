#!/usr/bin/env python3
"""Local-only broker for the fixed, read-only full ballet sync unit."""
import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UNIT = "maxnow-ballet-full-sync.service"
ORIGIN = "https://dash.maxnow.cn"
PATH = "/api/ballet/refresh"
COOLDOWN = 60


def unit_state():
    result = subprocess.run(
        ["/usr/bin/systemctl", "show", UNIT, "--property=ActiveState,Result,ExecMainStatus,ExecMainStartTimestampMonotonic"],
        capture_output=True, text=True, timeout=10, check=True,
    )
    return dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)


class Refresh:
    def __init__(self, inspect=unit_state, start=None, clock=time.monotonic, sleep=time.sleep):
        self.inspect = inspect
        self.start = start or self.start_unit
        self.clock, self.sleep = clock, sleep
        self.lock = threading.Lock()
        self.last_finished = float("-inf")
        self.state = {"status": "idle", "message": "等待刷新"}

    @staticmethod
    def start_unit():
        subprocess.run(
            ["/usr/bin/systemctl", "--no-ask-password", "start", "--no-block", UNIT],
            capture_output=True, timeout=10, check=True,
        )

    def snapshot(self):
        with self.lock:
            return dict(self.state)

    def request(self):
        with self.lock:
            if self.state["status"] == "running":
                return dict(self.state)
            if self.state["status"] in ("success", "error") and self.clock() - self.last_finished < COOLDOWN:
                return dict(self.state)
            self.state = {"status": "running", "message": "正在同步芭蕾整体数据…", "startedAt": datetime.now(timezone.utc).isoformat()}
            threading.Thread(target=self.run, daemon=True).start()
            return dict(self.state)

    def run(self):
        began = self.clock()
        status, message = "error", "同步失败，仍显示上次成功的数据；请稍后重试。"
        try:
            before = self.inspect()
            already_running = before.get("ActiveState") in ("activating", "active", "deactivating")
            if not already_running:
                self.start()
            started = already_running
            deadline = began + 330
            while self.clock() < deadline:
                current = self.inspect()
                stamp = current.get("ExecMainStartTimestampMonotonic")
                started = started or current.get("ActiveState") in ("activating", "active", "deactivating") or (stamp not in (None, "", "0") and stamp != before.get("ExecMainStartTimestampMonotonic"))
                if started and current.get("ActiveState") in ("inactive", "failed"):
                    if current.get("ActiveState") == "inactive" and current.get("Result") == "success" and current.get("ExecMainStatus") == "0":
                        status, message = "success", "芭蕾整体数据已刷新"
                    break
                self.sleep(2)
            else:
                message = "同步等待超时，仍显示上次成功的数据；可稍后刷新查看。"
        except (OSError, subprocess.SubprocessError):
            pass
        with self.lock:
            self.last_finished = self.clock()
            self.state = {**self.state, "status": status, "message": message,
                          "finishedAt": datetime.now(timezone.utc).isoformat(),
                          "durationSeconds": max(0, int(self.last_finished - began))}


refresh = Refresh()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def reply(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != PATH:
            return self.reply(404, {"status": "error"})
        self.reply(200, refresh.snapshot())

    def do_POST(self):
        if self.path != PATH:
            return self.reply(404, {"status": "error"})
        if self.headers.get("Origin") != ORIGIN or self.headers.get("X-MaxNow-Refresh") != "1":
            return self.reply(403, {"status": "error", "message": "刷新请求来源无效"})
        if self.headers.get("Content-Type") != "application/json" or self.headers.get("Content-Length") != "2":
            return self.reply(400, {"status": "error"})
        if self.rfile.read(2) != b"{}":
            return self.reply(400, {"status": "error"})
        self.reply(202, refresh.request())


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
