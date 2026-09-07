class CourseSection:
    def __init__(self, course_name, section, days, start_time, end_time):
        self.course_name = course_name
        self.section = section
        self.days = days
        self.start_time = start_time
        self.end_time = end_time

    def start_minutes(self):
        """Convert start time to minutes after midnight."""
        hours, minutes = map(int, self.start_time.split(":"))
        return hours * 60 + minutes

    def end_minutes(self):
        """Convert end time to minutes after midnight."""
        hours, minutes = map(int, self.end_time.split(":"))
        return hours * 60 + minutes

    def duration_minutes(self):
        """Return the class duration in minutes."""
        return self.end_minutes() - self.start_minutes()

    def __str__(self):
        return (
            f"{self.course_name} - Section {self.section}: "
            f"{self.days} {self.start_time}-{self.end_time}"
        )