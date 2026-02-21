import unittest
from src.simulation.broker import SimulatedBroker

class TestSimulatedBroker(unittest.TestCase):
    def setUp(self):
        self.broker = SimulatedBroker(initial_purse_nok=10000)

    def test_initialization(self):
        self.assertEqual(self.broker.purse, 10000)
        self.assertEqual(self.broker.initial_cash, 10000)

    def test_buy_execution(self):
        success, message = self.broker.execute_trade("AAPL", 1, 150, side='buy')
        self.assertTrue(success)
        # Cost: 150 + 0.1% commission (0.15) + 0.05% slippage (0.075) = 150.225
        expected_purse = 10000 - 150 - (150 * 0.001) - (150 * 0.0005)
        self.assertAlmostEqual(self.broker.purse, expected_purse, places=5)
        self.assertEqual(self.broker.positions["AAPL"]['qty'], 1)

    def test_insufficient_funds(self):
        success, message = self.broker.execute_trade("AAPL", 100, 200, side='buy')
        self.assertFalse(success)
        self.assertEqual(message, "Insufficient funds")

    def test_sell_execution(self):
        self.broker.execute_trade("AAPL", 2, 100, side='buy')
        success, message = self.broker.execute_trade("AAPL", 1, 110, side='sell')
        self.assertTrue(success)
        self.assertEqual(self.broker.positions["AAPL"]['qty'], 1)

if __name__ == "__main__":
    unittest.main()
