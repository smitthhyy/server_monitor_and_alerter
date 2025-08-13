# tests/test_process_monitor.py
import unittest
from unittest.mock import patch, MagicMock

from monitors.process import ProcessMonitor
from config import config

class ProcessMonitorTests(unittest.TestCase):
    @patch("alert.EmailAlerter.send")
    def test_process_consecutive_cycles_and_recovery(self, mock_send):
        # Configure: need 2 consecutive failures for first alert; repeats disabled for brevity
        thresholds = {
            "alert_repeat_cycles": 999,
            "alert_consecutive_cycles": {"Process": 2},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            # psutil.process_iter returns objects with .name()
            def iter_with(names):
                class P:
                    def __init__(self, n): self._n = n
                    def name(self): return self._n
                return [P(n) for n in names]

            mon = ProcessMonitor(["myservice"], min_count=1)

            with patch("psutil.process_iter", return_value=iter_with([])):
                mon.run()  # fail #1 (found=0, min=1) → no alert yet
            with patch("psutil.process_iter", return_value=iter_with([])):
                mon.run()  # fail #2 → first alert
            self.assertEqual(mock_send.call_count, 1)
            self.assertIn("[ALERT]", mock_send.call_args_list[-1][0][0])

            # Recovery only after prior alert
            with patch("psutil.process_iter", return_value=iter_with(["myservice"])):
                mon.run()  # healthy → RECOVERY expected
            self.assertEqual(mock_send.call_count, 2)
            self.assertIn("[RECOVERY]", mock_send.call_args_list[-1][0][0])

    @patch("alert.EmailAlerter.send")
    def test_process_no_recovery_if_no_prior_alert(self, mock_send):
        thresholds = {
            "alert_repeat_cycles": 999,
            "alert_consecutive_cycles": {"Process": 3},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            def iter_with(names):
                class P:
                    def __init__(self, n): self._n = n
                    def name(self): return self._n
                return [P(n) for n in names]

            mon = ProcessMonitor(["svc"], min_count=2)

            # Only 2 failure cycles? No, consecutive_required=3, so still no alert
            with patch("psutil.process_iter", return_value=iter_with(["svc"])):
                mon.run()  # found=1 (<2) → fail #1
            with patch("psutil.process_iter", return_value=iter_with(["svc"])):
                mon.run()  # fail #2

            # Now healthy before reaching required 3 fails
            with patch("psutil.process_iter", return_value=iter_with(["svc","svc"])):
                mon.run()  # recovery → should NOT send RECOVERY
            mock_send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
