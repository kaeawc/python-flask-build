import unittest
import zoneinfo


class DeloreanTestCase(unittest.TestCase):
    def setUp(self):
        # Hide the system tz database so zones must come from the tzdata package,
        # as on slim container images and Windows
        zoneinfo.reset_tzpath([])
        zoneinfo.ZoneInfo.clear_cache()

    def tearDown(self):
        zoneinfo.reset_tzpath()
        zoneinfo.ZoneInfo.clear_cache()

    def test_delorean_works_without_system_tz_database(self):
        import delorean
        from delorean import Delorean

        d = Delorean()

        # delorean 2.0 uses standard library timezones instead of pytz
        self.assertEqual(d.timezone, delorean.utc)
        self.assertIsInstance(d.timezone, zoneinfo.ZoneInfo)

        # delorean 2.0 returns Delorean objects from midnight
        self.assertIsInstance(d.midnight, Delorean)


if __name__ == "__main__":
    unittest.main()
