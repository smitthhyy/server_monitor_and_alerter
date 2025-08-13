# tests/test_alert_cycles.py
import unittest
from unittest.mock import patch, MagicMock

# We'll use a stub monitor to precisely drive status sequences without touching psutil.
from monitors.base_monitor import BaseMonitor
from config import config

class StubMonitor(BaseMonitor):
    name = "StubMonitor"

    def __init__(self, sequence, threshold=None):
        # sequence is a list of tuples: (breach_bool, value)
        super().__init__(threshold=threshold)
        self._seq = list(sequence)

    def check(self):
        # Pop next status/value; if sequence exhausted, return healthy
        if self._seq:
            return self._seq.pop(0)
        return (False, 0)


class AlertCyclesTests(unittest.TestCase):
    def setUp(self):
        # Minimal thresholds needed for BaseMonitor config lookups
        self.base_thresholds = {
            "alert_repeat_cycles": 3,   # small to make tests quick
            "alert_consecutive_cycles": {
                "StubMonitor": 3,       # require 3 consecutive errors before first alert
            }
        }

    @patch("alert.EmailAlerter.send")  # patch underlying send to avoid SES calls
    def test_no_recovery_if_no_alert(self, mock_send):
        # Configure thresholds for this test
        with patch.object(config, "thresholds", self.base_thresholds, create=False):
            # Only one failing cycle (< required 3) followed by a recovery
            seq = [
                (True,  100),  # 1st failure (no alert expected)
                (False,  50),  # recovery - no prior alert, so no RECOVERY expected
            ]
            mon = StubMonitor(seq, threshold=80)

            mon.run()  # fail #1
            mon.run()  # recover

        # No alerts should have been sent at all
        mock_send.assert_not_called()

    @patch("alert.EmailAlerter.send")
    def test_first_alert_after_consecutive_required(self, mock_send):
        with patch.object(config, "thresholds", self.base_thresholds, create=False):
            seq = [
                (True,  100),  # fail #1
                (True,  100),  # fail #2
                (True,  100),  # fail #3 → should trigger first alert
            ]
            mon = StubMonitor(seq, threshold=80)

            mon.run()
            mon.run()
            # No alert yet
            mock_send.assert_not_called()

            mon.run()  # third consecutive fail
            self.assertEqual(mock_send.call_count, 1)
            args, kwargs = mock_send.call_args
            self.assertIn("[ALERT]", args[0])

    @patch("alert.EmailAlerter.send")
    def test_repeat_alert_after_repeat_cycles(self, mock_send):
        # Require 2 for repeat to show faster in test
        thresholds = {
            "alert_repeat_cycles": 2,
            "alert_consecutive_cycles": {"StubMonitor": 1},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            # Fails continuously for several cycles
            seq = [
                (True,  100),  # fail #1 → first alert (consecutive_required=1)
                (True,  100),  # fail #2 → repeat alert (repeat_cycles=2)
                (True,  100),  # fail #1 after reset (no alert yet)
                (True,  100),  # fail #2 → repeat alert again
            ]
            mon = StubMonitor(seq, threshold=80)

            mon.run()  # first alert
            mon.run()  # repeat alert
            mon.run()  # counter reset; no alert
            mon.run()  # repeat alert again

            # Expect 3 alerts total: first + two repeats
            self.assertEqual(mock_send.call_count, 3)
            for call in mock_send.call_args_list:
                subject = call[0][0]
                self.assertIn("[ALERT]", subject)

    @patch("alert.EmailAlerter.send")
    def test_recovery_only_after_alert_sent(self, mock_send):
        thresholds = {
            "alert_repeat_cycles": 10,
            "alert_consecutive_cycles": {"StubMonitor": 2},
        }
        with patch.object(config, "thresholds", thresholds, create=False):
            seq = [
                (True,  100),  # fail #1 (no alert yet, need 2)
                (False,  50),  # recovery → no RECOVERY because no alert was sent
                (True,  100),  # fail #1 again
                (True,  100),  # fail #2 → first alert sent here
                (False,  50),  # recovery → RECOVERY should be sent
            ]
            mon = StubMonitor(seq, threshold=80)

            mon.run()
            mon.run()
            mon.run()
            mon.run()
            # At this point, 1 alert should have been sent
            self.assertEqual(mock_send.call_count, 1)
            self.assertIn("[ALERT]", mock_send.call_args_list[-1][0][0])

            mon.run()
            # Now a recovery notice is sent
            self.assertEqual(mock_send.call_count, 2)
            self.assertIn("[RECOVERY]", mock_send.call_args_list[-1][0][0])


if __name__ == "__main__":
    unittest.main()
