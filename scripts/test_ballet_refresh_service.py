import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import Mock, patch

import ballet_refresh_service as service


def state(active="inactive", stamp="1", result="success", exit_code="0"):
    return {"ActiveState": active, "ExecMainStartTimestampMonotonic": stamp, "Result": result, "ExecMainStatus": exit_code}


class RefreshTests(unittest.TestCase):
    def test_waits_for_new_unit_execution_before_success(self):
        inspect = Mock(side_effect=[state(), state(), state("activating", "2"), state(stamp="2")])
        start, sleep = Mock(), Mock()
        broker = service.Refresh(inspect, start, sleep=sleep)
        broker.run()
        self.assertEqual(broker.snapshot()["status"], "success")
        start.assert_called_once_with()
        self.assertEqual(sleep.call_count, 2)

    def test_joins_existing_sync_without_starting_again(self):
        start = Mock()
        broker = service.Refresh(Mock(side_effect=[state("activating"), state()]), start)
        broker.run()
        start.assert_not_called()
        self.assertEqual(broker.snapshot()["status"], "success")

    def test_failed_or_lock_contended_sync_is_not_success(self):
        broker = service.Refresh(Mock(side_effect=[state(), state("failed", "2", "exit-code", "1")]), Mock())
        broker.run()
        self.assertEqual(broker.snapshot()["status"], "error")

    def test_duplicate_requests_share_worker_and_recent_result(self):
        broker = service.Refresh(clock=lambda: 10)
        with patch.object(service.threading, "Thread") as thread:
            self.assertEqual(broker.request()["status"], "running")
            broker.request()
            thread.assert_called_once()
            broker.state = {"status": "success", "message": "done"}
            broker.last_finished = 9
            self.assertEqual(broker.request()["status"], "success")
            thread.assert_called_once()

    def test_timeout_is_error(self):
        broker = service.Refresh(Mock(return_value=state()), Mock(), clock=Mock(side_effect=[0, 331, 332]))
        broker.run()
        self.assertEqual(broker.snapshot()["status"], "error")

    def test_http_rejects_cross_origin_and_arbitrary_payload(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), service.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection(*server.server_address)
            with patch.object(service.refresh, "request", return_value={"status": "running"}) as request:
                for origin, body, expected in [("https://evil.example", "{}", 403), (service.ORIGIN, '{"unit":"other"}', 400), (service.ORIGIN, "{}", 202)]:
                    conn.request("POST", service.PATH, body, {"Origin": origin, "Content-Type": "application/json", "X-MaxNow-Refresh": "1"})
                    response = conn.getresponse()
                    self.assertEqual(response.status, expected)
                    response.read()
                request.assert_called_once_with()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
