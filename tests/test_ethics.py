import unittest
from src.intelligence.social import EthicalFilter

class TestEthicalFilter(unittest.TestCase):
    def setUp(self):
        # Initialize the filter with some mock blocked entities
        self.filter = EthicalFilter(
            blocked_companies=["BAD_CO"],
            blocked_countries=["NOT_A_GOOD_PLACE"],
            blocked_segments=["Weapons"]
        )

    def test_allowed_asset(self):
        # This asset should pass all checks
        asset = {"ticker": "GOOD_CO", "country": "Norway", "segment": "Tech"}
        allowed, reason = self.filter.is_allowed(asset)
        self.assertTrue(allowed)
        self.assertEqual(reason, "Asset is ethically cleared.")

    def test_blocked_company(self):
        # This asset should be blocked due to the company name
        asset = {"ticker": "BAD_CO", "country": "Norway", "segment": "Tech"}
        allowed, reason = self.filter.is_allowed(asset)
        self.assertFalse(allowed)
        self.assertIn("company", reason.lower())

    def test_blocked_country(self):
        # This asset should be blocked due to the country
        asset = {"ticker": "GOOD_CO", "country": "NOT_A_GOOD_PLACE", "segment": "Tech"}
        allowed, reason = self.filter.is_allowed(asset)
        self.assertFalse(allowed)
        self.assertIn("country", reason.lower())

    def test_blocked_segment(self):
        # This asset should be blocked due to the industry segment
        asset = {"ticker": "GOOD_CO", "country": "Norway", "segment": "Weapons"}
        allowed, reason = self.filter.is_allowed(asset)
        self.assertFalse(allowed)
        self.assertIn("segment", reason.lower())

if __name__ == "__main__":
    unittest.main()
