import unittest
from fluxion.utils.retry import retry

class TestRetry(unittest.TestCase):
    def test_successful_execution(self):
        @retry(attempts=3)
        def always_succeed():
            return "success"

        self.assertEqual(always_succeed(), "success")

    def test_retry_on_failure(self):
        counter = {"attempts": 0}

        @retry(attempts=3)
        def succeed_on_third_try():
            counter["attempts"] += 1
            if counter["attempts"] < 3:
                raise ValueError("Failure")
            return "success"

        self.assertEqual(succeed_on_third_try(), "success")

    def test_exhaust_retries(self):
        @retry(attempts=3)
        def always_fail():
            raise ValueError("Failure")

        with self.assertRaises(ValueError):
            always_fail()

if __name__ == "__main__":
    unittest.main()
