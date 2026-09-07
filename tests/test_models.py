import unittest

from models import CourseSection


class TestCourseSection(unittest.TestCase):

    def setUp(self):
        self.section = CourseSection(
            "CSE 360",
            "1",
            "MW",
            "10:30",
            "11:45"
        )

    def test_start_minutes(self):
        self.assertEqual(
            self.section.start_minutes(),
            630
        )

    def test_end_minutes(self):
        self.assertEqual(
            self.section.end_minutes(),
            705
        )

    def test_duration_minutes(self):
        self.assertEqual(
            self.section.duration_minutes(),
            75
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.section),
            "CSE 360 - Section 1: MW 10:30-11:45"
        )


if __name__ == "__main__":
    unittest.main()