import csv
from models import CourseSection


def load_courses(filename):
    """
    Load course sections from a CSV file.

    Returns a dictionary where each course maps
    to a list of available sections.
    """

    courses = {}

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            section = CourseSection(
                row["course"],
                row["section"],
                row["days"],
                row["start"],
                row["end"]
            )

            course_name = row["course"]

            if course_name not in courses:
                courses[course_name] = []

            courses[course_name].append(section)

    return courses