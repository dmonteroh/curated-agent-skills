# Automation Testing

```python
import unittest
from unittest.mock import patch, MagicMock
from self_healing import cleanup_disk, restart_service

class TestSelfHealing(unittest.TestCase):
    """Test self-healing automation."""

    @patch('subprocess.run')
    def test_disk_cleanup_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = cleanup_disk()
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_service_restart_with_retry(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(returncode=0),
        ]
        result = restart_service()
        self.assertTrue(result)
```

## Usage

1. Save the tests alongside the automation script.
2. Run `python -m unittest automation_tests.py`.

## Verification

- Confirm tests pass with expected retries.
- Review test output for failures before deploying automation.
