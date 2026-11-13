from itertools import product


def sections_conflict(section1, section2):
    """
    Determine whether two course sections overlap.
    """

    common_days = set(section1.days) & set(section2.days)

    if not common_days:
        return False

    start1 = section1.start_minutes()
    end1 = section1.end_minutes()

    start2 = section2.start_minutes()
    end2 = section2.end_minutes()

    return start1 < end2 and start2 < end1


def schedule_is_valid(schedule):
    """
    Check whether any two sections in a schedule conflict.
    """

    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            if sections_conflict(schedule[i], schedule[j]):
                return False

    return True


def generate_schedules(course_sections):
    """
    Generate every possible combination of course sections
    and return only conflict-free schedules.
    """

    all_combinations = product(*course_sections.values())

    valid_schedules = []

    for combination in all_combinations:
        if schedule_is_valid(combination):
            valid_schedules.append(combination)

    return valid_schedules


def time_to_minutes(time):
    """
    Convert HH:MM into minutes after midnight.
    """

    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def get_days(schedule):
    """
    Return the unique days on which the schedule has classes.
    """

    days = set()

    for section in schedule:
        for day in section.days:
            days.add(day)

    return days


def get_day_sections(schedule, day):
    """
    Return sections occurring on a specific day.
    """

    sections = [
        section
        for section in schedule
        if day in section.days
    ]

    return sorted(
        sections,
        key=lambda section: section.start_minutes()
    )


def calculate_total_gaps(schedule):
    """
    Calculate the total number of minutes spent
    between classes on the same day.
    """

    total_gap = 0

    days = ["M", "T", "W", "R", "F"]

    for day in days:

        day_sections = get_day_sections(
            schedule,
            day
        )

        for i in range(len(day_sections) - 1):

            current = day_sections[i]
            next_section = day_sections[i + 1]

            gap = (
                next_section.start_minutes()
                - current.end_minutes()
            )

            if gap > 0:
                total_gap += gap

    return total_gap


def calculate_gap_penalty(schedule):
    """
    Penalize large gaps between classes.
    """

    penalty = 0

    days = ["M", "T", "W", "R", "F"]

    for day in days:

        day_sections = get_day_sections(
            schedule,
            day
        )

        for i in range(len(day_sections) - 1):

            current = day_sections[i]
            next_section = day_sections[i + 1]

            gap = (
                next_section.start_minutes()
                - current.end_minutes()
            )

            if gap <= 30:
                continue

            if gap <= 60:
                penalty += 2
            elif gap <= 90:
                penalty += 5
            elif gap <= 120:
                penalty += 8
            else:
                penalty += 12

    return penalty


def calculate_days_penalty(schedule):
    """
    Penalize schedules requiring more days on campus.
    """

    number_of_days = len(get_days(schedule))

    if number_of_days <= 2:
        return 0

    if number_of_days == 3:
        return 3

    if number_of_days == 4:
        return 7

    return 12


def calculate_daily_load_penalty(schedule, max_classes):
    """
    Penalize schedules that exceed the preferred
    maximum number of classes per day.
    """

    penalty = 0

    days = ["M", "T", "W", "R", "F"]

    for day in days:

        classes_that_day = [
            section
            for section in schedule
            if day in section.days
        ]

        if len(classes_that_day) > max_classes:
            extra_classes = (
                len(classes_that_day) - max_classes
            )

            penalty += extra_classes * 8

    return penalty


def calculate_schedule_score(schedule, preferences):
    """
    Calculate an overall schedule score from 0 to 100.
    """

    score = 100

    preferred_start = preferences.get(
        "preferred_start",
        "09:00"
    )

    preferred_end = preferences.get(
        "preferred_end",
        "16:00"
    )

    avoid_fridays = preferences.get(
        "avoid_fridays",
        False
    )

    max_classes_per_day = preferences.get(
        "max_classes_per_day",
        3
    )

    preferred_start_minutes = time_to_minutes(
        preferred_start
    )

    preferred_end_minutes = time_to_minutes(
        preferred_end
    )

    for section in schedule:

        start = section.start_minutes()
        end = section.end_minutes()

        if start < preferred_start_minutes:
            score -= 5

        if end > preferred_end_minutes:
            score -= 5

        if avoid_fridays and "F" in section.days:
            score -= 10

    score -= calculate_gap_penalty(schedule)

    score -= calculate_days_penalty(schedule)

    score -= calculate_daily_load_penalty(
        schedule,
        max_classes_per_day
    )

    return max(0, min(score, 100))


def get_schedule_analysis(schedule, preferences):
    """
    Generate a human-readable analysis explaining
    the strengths and weaknesses of a schedule.
    """

    preferred_start = time_to_minutes(
        preferences.get("preferred_start", "09:00")
    )

    preferred_end = time_to_minutes(
        preferences.get("preferred_end", "16:00")
    )

    avoid_fridays = preferences.get(
        "avoid_fridays",
        False
    )

    max_classes = preferences.get(
        "max_classes_per_day",
        3
    )

    analysis = []

    # Check class times.
    outside_preferred_hours = []

    for section in schedule:

        if section.start_minutes() < preferred_start:
            outside_preferred_hours.append(section)

        elif section.end_minutes() > preferred_end:
            outside_preferred_hours.append(section)

    if not outside_preferred_hours:
        analysis.append("✓ All classes within preferred hours")
    else:
        analysis.append(
            f"⚠ {len(outside_preferred_hours)} "
            "class(es) outside preferred hours"
        )

    # Check Friday.
    friday_classes = [
        section
        for section in schedule
        if "F" in section.days
    ]

    if avoid_fridays:

        if not friday_classes:
            analysis.append("✓ No Friday classes")
        else:
            analysis.append(
                f"⚠ {len(friday_classes)} Friday class(es)"
            )

    # Days on campus.
    number_of_days = len(get_days(schedule))

    analysis.append(
        f"✓ {number_of_days} day(s) on campus"
    )

    # Schedule gaps.
    total_gaps = calculate_total_gaps(schedule)

    if total_gaps == 0:
        analysis.append("✓ No gaps between classes")
    elif total_gaps <= 60:
        analysis.append(
            f"✓ {total_gaps} minutes of total gaps"
        )
    else:
        analysis.append(
            f"⚠ {total_gaps} minutes of total gaps"
        )

    # Daily workload.
    days = ["M", "T", "W", "R", "F"]

    largest_daily_load = 0

    for day in days:

        count = len(
            [
                section
                for section in schedule
                if day in section.days
            ]
        )

        largest_daily_load = max(
            largest_daily_load,
            count
        )

    if largest_daily_load <= max_classes:
        analysis.append(
            f"✓ Maximum of {largest_daily_load} "
            "classes in one day"
        )
    else:
        analysis.append(
            f"⚠ Up to {largest_daily_load} "
            "classes in one day"
        )

    return analysis


def rank_schedules(schedules, preferences):
    """
    Rank schedules from highest score to lowest score.
    """

    scored_schedules = []

    for schedule in schedules:

        score = calculate_schedule_score(
            schedule,
            preferences
        )

        scored_schedules.append(
            (score, schedule)
        )

    scored_schedules.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return scored_schedules