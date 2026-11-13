import unittest
import os
import tempfile

from data_loader import load_courses


class TestDataLoader(unittest.TestCase):

    def test_load_courses(self):

        csv_data = """course,section,days,start,end
CSE 360,1,MW,10:30,11:45
CSE 360,2,TR,09:00,10:15
MAT 343,1,MW,13:00,14:15
"""

        # Create a temporary CSV file for testing.
        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".csv"
        ) as file:

            file.write(csv_data)
            filename = file.name

        try:

            courses = load_courses(filename)

            self.assertEqual(
                len(courses),
                2
            )

            self.assertEqual(
                len(courses["CSE 360"]),
                2
            )

            self.assertEqual(
                len(courses["MAT 343"]),
                1
            )

            self.assertEqual(
                courses["CSE 360"][0].start_time,
                "10:30"
            )

        finally:

            os.remove(filename)


if __name__ == "__main__":
    unittest.main()