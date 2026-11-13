# Smart Schedule Builder

Pick your courses, describe what a good week looks like, and get every conflict-free timetable **ranked, with an explanation behind each score**.

## Why I Built It

Registering for classes means juggling section times, checking for overlaps, avoiding long gaps, and trying to keep certain days free. I wanted to build a tool that checks possible combinations of course sections and explains which schedule best matches a student's preferences.

The project started as a Python command-line program with automated tests. I then expanded it into a browser-based application so users can build schedules without installing anything.

## Features

- Finds combinations of course sections with no time conflicts
- Scores schedules out of 100 and explains point deductions
- Supports preferred earliest start and latest finish times
- Allows users to avoid Friday classes
- Penalizes long gaps between classes and unnecessary campus days
- Respects a maximum number of classes per day
- Displays schedules in a weekly calendar grid
- Includes copy and print options
- Supports custom course data through CSV uploads or pasted text

## How to Use

1. Open `index.html` in a web browser.
2. Select the courses you want to include.
3. Adjust scheduling preferences, including start time, end time, Fridays, and maximum classes per day.
4. Click **Build Schedules** to generate and rank possible schedules.
5. Compare the results and choose the schedule that works best.

## Using Custom Course Data

The application supports uploading a CSV file or pasting course information.

Required columns:

| Column | Description | Example |
|---|---|---|
| `course` | Course name | `CSE 360` |
| `section` | Section number | `1` |
| `days` | Meeting days (M, T, W, R, F; R = Thursday) | `TR` |
| `start` | Start time in 24-hour format | `09:00` |
| `end` | End time in 24-hour format | `10:15` |

Example:

```csv
course,section,days,start,end
CSE 360,1,MW,10:30,11:45
CSE 360,2,TR,09:00,10:15
MAT 343,1,MW,13:00,14:15
```

A sample dataset is included in `sample-courses.csv`.

## Project Structure

```text
smart-schedule-builder/
├── index.html
├── styles.css
├── script.js
├── sample-courses.csv
├── python/
│   ├── main.py
│   ├── models.py
│   ├── data_loader.py
│   ├── scheduler.py
│   ├── courses.csv
│   └── tests/
└── README.md
```

## Python Version

The original Python implementation is included in the `python/` directory. It contains the scheduling logic, conflict detection, schedule scoring, and automated unit tests.

To run the command-line version:

```bash
cd python
python3 main.py
```

To run the tests:

```bash
python3 -m unittest discover
```

## Technologies Used

- HTML
- CSS
- JavaScript
- Python 3
- Object-oriented programming
- CSV data processing
- Automated testing with `unittest`

## Future Improvements

- Integrate course information from university catalogs or APIs
- Add course prerequisites and preferred days
- Improve workload balancing
- Export schedules to calendar formats
- Allow users to save and compare favorite schedules