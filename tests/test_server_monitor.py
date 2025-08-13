# tests/test_server_monitor.py
import unittest
from unittest.mock import patch, MagicMock

from monitors.server import ServerMonitor
from config import config

class ServerMonitorTests(unittest.TestCase):
    @patch("alert.EmailAlerter.send")
    def test_server_consecutive_cycles_and_recovery(self, mock_send):
        thresholds = {
            "alert_repeat_cycles": 999,
            "alert_consecutive_cycles": {"ServerStatus": 2},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            mon = ServerMonitor("https://example.com/health")

            # Down twice → first alert on second check
            with patch("requests.get", side_effect=Exception("down")):
                mon.run()  # fail #1
            with patch("requests.get", side_effect=Exception("down")):
                mon.run()  # fail #2 → alert
            self.assertEqual(mock_send.call_count, 1)
            self.assertIn("[ALERT]", mock_send.call_args_list[-1][0][0])

            # Recovery: HTTP 200
            class R:
                status_code = 200
            with patch("requests.get", return_value=R()):
                mon.run()  # recovery → RECOVERY
            self.assertEqual(mock_send.call_count, 2)
            self.assertIn("[RECOVERY]", mock_send.call_args_list[-1][0][0])

    @patch("alert.EmailAlerter.send")
    def test_server_no_recovery_without_prior_alert(self, mock_send):
        thresholds = {
            "alert_repeat_cycles": 999,
            "alert_consecutive_cycles": {"ServerStatus": 3},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            mon = ServerMonitor("https://example.com/health")

            # Two failures (not enough for first alert), then recovery
            with patch("requests.get", side_effect=Exception()):
                mon.run()  # fail #1
            with patch("requests.get", side_effect=Exception()):
                mon.run()  # fail #2
            class R:
                status_code = 200
            with patch("requests.get", return_value=R()):
                mon.run()  # healthy → should NOT send RECOVERY
            mock_send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
