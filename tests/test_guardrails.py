import unittest
from src.security.guardrails import Guardrail

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        self.guard = Guardrail(
            max_drawdown_pct=0.10, 
            max_position_size_pct=0.05,
            restricted_assets=["RESTRICTED_CO"]
        )

    def test_safe_trade(self):
        # Portfolio: 100k, Trade: 1k (1%) -> Allowed
        allowed, reason = self.guard.check_trade(100000, 100000, 1000, "AAPL", {})
        self.assertTrue(allowed)

    def test_position_size_limit(self):
        # Portfolio: 100k, Trade: 6k (6%) -> Blocked (Limit is 5%)
        allowed, reason = self.guard.check_trade(100000, 100000, 6000, "AAPL", {})
        self.assertFalse(allowed)
        self.assertIn("exceeds 5.0%", reason)

    def test_drawdown_limit(self):
        # Simulate peak portfolio at 100k
        self.guard.check_trade(100000, 100000, 100, "AAPL", {})
        
        # Portfolio drops to 89k (11% drawdown) -> Trading Halted
        allowed, reason = self.guard.check_trade(89000, 89000, 100, "AAPL", {})
        self.assertFalse(allowed)
        self.assertIn("Max drawdown", reason)

    def test_restricted_asset(self):
        allowed, reason = self.guard.check_trade(100000, 100000, 100, "RESTRICTED_CO", {})
        self.assertFalse(allowed)
        self.assertIn("restricted list", reason)

if __name__ == "__main__":
    unittest.main()
