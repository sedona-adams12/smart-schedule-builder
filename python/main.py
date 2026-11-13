import os

from data_loader import load_courses
from scheduler import (
    generate_schedules,
    rank_schedules,
    get_schedule_analysis
)


def get_user_courses(available_courses):
    """
    Ask the user which courses they want to schedule.
    """

    print("\nAvailable Courses:")

    course_list = list(available_courses.keys())

    for number, course in enumerate(course_list, start=1):
        print(f"{number}. {course}")

    while True:

        user_input = input(
            "\nEnter the course numbers you want to take "
            "(example: 1, 2, 3): "
        )

        try:

            selections = [
                int(number.strip())
                for number in user_input.split(",")
            ]

            if not selections:
                print("Please select at least one course.")
                continue

            if any(
                number < 1 or number > len(course_list)
                for number in selections
            ):
                print("One or more selections are invalid.")
                continue

            selected_courses = {}

            for number in selections:

                course_name = course_list[number - 1]

                if course_name not in selected_courses:
                    selected_courses[course_name] = (
                        available_courses[course_name]
                    )

            return selected_courses

        except ValueError:

            print(
                "Please enter course numbers separated by commas."
            )


def get_time_preference(prompt, default):
    """
    Ask the user for a preferred time.
    """

    while True:

        user_input = input(
            f"{prompt} [{default}]: "
        ).strip()

        if not user_input:
            return default

        try:

            hours, minutes = map(
                int,
                user_input.split(":")
            )

            if 0 <= hours <= 23 and 0 <= minutes <= 59:
                return f"{hours:02d}:{minutes:02d}"

            print(
                "Please enter a valid time such as 09:00."
            )

        except ValueError:

            print(
                "Please enter a valid time such as 09:00."
            )


def get_yes_no(prompt):
    """
    Ask the user a yes/no question.
    """

    while True:

        answer = input(
            f"{prompt} (yes/no): "
        ).strip().lower()

        if answer in ["yes", "y"]:
            return True

        if answer in ["no", "n"]:
            return False

        print("Please enter yes or no.")


def get_max_classes_per_day():
    """
    Ask the user for the maximum preferred
    number of classes per day.
    """

    while True:

        user_input = input(
            "Maximum preferred classes per day [3]: "
        ).strip()

        if not user_input:
            return 3

        try:

            value = int(user_input)

            if value >= 1:
                return value

            print(
                "Please enter a number greater than 0."
            )

        except ValueError:

            print(
                "Please enter a whole number such as 3."
            )


def display_schedule(
    number,
    score,
    schedule,
    preferences
):
    """
    Display a schedule and explain its score.
    """

    print(
        f"\nSchedule {number} | Score: {score}/100"
    )

    print("-" * 55)

    for section in schedule:
        print(f"  {section}")

    print("\nAnalysis:")

    analysis = get_schedule_analysis(
        schedule,
        preferences
    )

    for item in analysis:
        print(f"  {item}")


def main():
    """
    Run the Smart Schedule Builder.
    """

    print("=" * 55)
    print("             SMART SCHEDULE BUILDER")
    print("=" * 55)

    # -----------------------------------------
    # LOAD COURSE DATA
    # -----------------------------------------

    try:

        csv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "courses.csv"
        )

        all_courses = load_courses(csv_path)

    except FileNotFoundError:

        print("\nError: courses.csv was not found.")

        print(
            "Make sure courses.csv is in the same "
            "folder as main.py."
        )

        return

    print(
        f"\nSuccessfully loaded {len(all_courses)} courses."
    )

    # -----------------------------------------
    # SELECT COURSES
    # -----------------------------------------

    selected_courses = get_user_courses(
        all_courses
    )

    print("\nSelected Courses:")

    for course in selected_courses:
        print(f"  ✓ {course}")

    # -----------------------------------------
    # GET PREFERENCES
    # -----------------------------------------

    print("\n" + "-" * 55)
    print("SCHEDULE PREFERENCES")
    print("-" * 55)

    preferred_start = get_time_preference(
        "Earliest preferred class time",
        "09:00"
    )

    preferred_end = get_time_preference(
        "Latest preferred class time",
        "16:00"
    )

    avoid_fridays = get_yes_no(
        "Avoid Friday classes?"
    )

    max_classes_per_day = (
        get_max_classes_per_day()
    )

    preferences = {
        "preferred_start": preferred_start,
        "preferred_end": preferred_end,
        "avoid_fridays": avoid_fridays,
        "max_classes_per_day": max_classes_per_day
    }

    # -----------------------------------------
    # GENERATE SCHEDULES
    # -----------------------------------------

    print("\nGenerating schedules...")

    valid_schedules = generate_schedules(
        selected_courses
    )

    if not valid_schedules:

        print("\nNo valid schedules were found.")

        print(
            "Try selecting different courses "
            "or sections."
        )

        return

    # -----------------------------------------
    # RANK SCHEDULES
    # -----------------------------------------

    ranked_schedules = rank_schedules(
        valid_schedules,
        preferences
    )

    # -----------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------

    print("\n" + "=" * 55)
    print("                    RESULTS")
    print("=" * 55)

    print(
        f"\nFound {len(valid_schedules)} "
        "valid schedules."
    )

    print("\nTop Schedule Options:")
    print("-" * 55)

    for number, (score, schedule) in enumerate(
        ranked_schedules[:5],
        start=1
    ):

        display_schedule(
            number,
            score,
            schedule,
            preferences
        )

    # -----------------------------------------
    # RECOMMENDATION
    # -----------------------------------------

    best_score, best_schedule = (
        ranked_schedules[0]
    )

    print("\n" + "=" * 55)
    print("                 RECOMMENDATION")
    print("=" * 55)

    print(
        f"\nBest schedule: "
        f"Score {best_score}/100"
    )

    print(
        "\nThis schedule received the highest score "
        "based on your selected preferences."
    )

    for section in best_schedule:
        print(f"  ✓ {section}")

    print("\n" + "=" * 55)
    print("Schedule generation complete!")
    print("=" * 55)


if __name__ == "__main__":
    main()