import unittest

from models import CourseSection
from scheduler import (
    sections_conflict,
    schedule_is_valid,
    generate_schedules,
    calculate_total_gaps,
    calculate_schedule_score,
    rank_schedules
)


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.morning_class = CourseSection(
            "CSE 360",
            "1",
            "MW",
            "10:00",
            "11:00"
        )

        self.overlapping_class = CourseSection(
            "CSE 365",
            "1",
            "MW",
            "10:30",
            "11:30"
        )

        self.back_to_back_class = CourseSection(
            "MAT 343",
            "1",
            "MW",
            "11:00",
            "12:00"
        )

        self.different_day_class = CourseSection(
            "CSE 310",
            "1",
            "TR",
            "10:30",
            "11:30"
        )

    def test_overlapping_classes_conflict(self):
        result = sections_conflict(
            self.morning_class,
            self.overlapping_class
        )

        self.assertTrue(result)

    def test_back_to_back_classes_do_not_conflict(self):
        result = sections_conflict(
            self.morning_class,
            self.back_to_back_class
        )

        self.assertFalse(result)

    def test_different_day_classes_do_not_conflict(self):
        result = sections_conflict(
            self.morning_class,
            self.different_day_class
        )

        self.assertFalse(result)

    def test_valid_schedule(self):
        schedule = (
            self.morning_class,
            self.back_to_back_class
        )

        self.assertTrue(
            schedule_is_valid(schedule)
        )

    def test_invalid_schedule(self):
        schedule = (
            self.morning_class,
            self.overlapping_class
        )

        self.assertFalse(
            schedule_is_valid(schedule)
        )

    def test_generate_schedules(self):

        courses = {
            "CSE 360": [
                self.morning_class
            ],
            "CSE 365": [
                self.overlapping_class,
                self.different_day_class
            ]
        }

        schedules = generate_schedules(courses)

        # Only the different-day option should be valid.
        self.assertEqual(
            len(schedules),
            1
        )

    def test_calculate_total_gaps(self):

        schedule = (
            self.morning_class,
            CourseSection(
                "MAT 343",
                "1",
                "MW",
                "12:00",
                "13:00"
            )
        )

        # There is a 60-minute gap on both Monday and Wednesday.
        # Total weekly gap = 120 minutes.
        self.assertEqual(
            calculate_total_gaps(schedule),
            120
        )

    def test_schedule_score_is_valid_range(self):

        schedule = (
            self.morning_class,
            self.back_to_back_class
        )

        preferences = {
            "preferred_start": "09:00",
            "preferred_end": "16:00",
            "avoid_fridays": True,
            "max_classes_per_day": 3
        }

        score = calculate_schedule_score(
            schedule,
            preferences
        )

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_rank_schedules(self):

        good_schedule = (
            self.morning_class,
            self.back_to_back_class
        )

        bad_schedule = (
            self.morning_class,
            CourseSection(
                "MAT 343",
                "1",
                "MW",
                "14:00",
                "15:00"
            )
        )

        schedules = [
            bad_schedule,
            good_schedule
        ]

        preferences = {
            "preferred_start": "09:00",
            "preferred_end": "16:00",
            "avoid_fridays": True,
            "max_classes_per_day": 3
        }

        ranked = rank_schedules(
            schedules,
            preferences
        )

        # The highest-scoring schedule should come first.
        self.assertGreaterEqual(
            ranked[0][0],
            ranked[1][0]
        )


if __name__ == "__main__":
    unittest.main()