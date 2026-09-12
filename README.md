Smart Schedule Builder
A Python-based course scheduling tool that generates and ranks possible class schedules based on course availability and student preferences.
Features
	•	Loads course sections from a CSV file
	•	Detects conflicts between classes
	•	Generates all valid schedule combinations
	•	Scores schedules based on user preferences
	•	Penalizes large gaps between classes
	•	Penalizes schedules with too many campus days
	•	Limits the number of classes per day
	•	Supports preferred start and end times
	•	Can avoid Friday classes
	•	Provides a schedule analysis explaining strengths and weaknesses
	•	Includes automated unit tests
How It Works
The program takes available course sections from courses.csv and generates possible combinations.
Each schedule is checked for conflicts first. Valid schedules are then scored using factors such as:
	•	Preferred class times
	•	Friday classes
	•	Gaps between classes
	•	Number of days on campus
	•	Number of classes per day
The schedules are ranked from highest to lowest score, and the highest-scoring schedule is recommended.
Project Structure
smart-schedule-builder/
│
├── main.py
├── models.py
├── data_loader.py
├── scheduler.py
├── courses.csv
├── README.md
├── .gitignore
│
└── tests/
    ├── test_models.py
    ├── test_scheduler.py
    └── test_data_loader.py
Technologies
	•	Python
	•	Object-Oriented Programming
	•	CSV data processing
	•	Constraint-based scheduling
	•	Unit testing with unittest
Running the Project
Make sure Python 3 is installed.
Run:
python3 main.py
The program will ask for:
	1	Courses to include
	2	Earliest preferred class time
	3	Latest preferred class time
	4	Whether to avoid Friday classes
	5	Maximum preferred classes per day
It will then generate and rank the available schedules.
Running Tests
Run all automated tests with:
python3 -m unittest discover
Example Use Case
A student can use the tool to compare different combinations of course sections and find a schedule that minimizes conflicts, long gaps, and unnecessary days on campus while matching their preferred class times.
Future Improvements
	•	Add a graphical user interface
	•	Import real course data automatically
	•	Add course prerequisites
	•	Support preferred days
	•	Add workload balancing
	•	Export schedules to a calendar format
	•	Allow users to save and compare favorite schedules
