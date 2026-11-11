# AI Student Record Manager

A beginner-friendly local web application for teachers. It manages student marks, calculates results, stores records in JSON, and uses the Groq API to generate academic feedback and personalized study tips.

## Features

- Add, view, search, update and delete student records.
- Student IDs remain unchanged during updates.
- Automatic total, average percentage and grade calculation.
- Local JSON persistence in `students.json`.
- Groq-powered **Analyze Performance** and **Generate Study Tips**.
- The AI receives only class/semester, subject names, marks, total, average and grade. Student name and ID are not included in AI prompts.
- Responsive green-and-white interface.

## Technologies

Python 3, Flask, Groq Python SDK, python-dotenv, HTML5, CSS3, JavaScript, Fetch API and JSON.

## Project structure

```text
AI_Student_Record_Manager_Web/
├── app.py
├── ai_helper.py
├── students.json
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── templates/
    └── index.html
```

## Requirements

- Windows computer (the commands below use Windows syntax)
- Python 3
- Visual Studio Code
- Google Chrome or another modern browser
- Internet connection and a Groq API key for AI features

Student management and result calculations work without a Groq key; only the AI buttons require it.

## Installation and setup

1. Install Python from <https://www.python.org/downloads/>. During installation, enable **Add Python to PATH**.
2. Extract the project ZIP and open the `AI_Student_Record_Manager_Web` folder in VS Code.
3. Open **Terminal → New Terminal** and confirm that the terminal is in the project folder.
4. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

5. Activate it in PowerShell:

   ```powershell
   venv\Scripts\Activate
   ```

   If PowerShell activation is blocked by your institution's policy, use Command Prompt and run `venv\Scripts\activate.bat`. Do not weaken security settings without permission.

6. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

## Configure Groq

1. Sign in at <https://console.groq.com/keys> and create an API key.
2. Copy `.env.example` and rename the copy to `.env` in the project root.
3. Open `.env` and add your key:

   ```dotenv
   GROQ_API_KEY=your_actual_groq_api_key
   GROQ_MODEL=
   ```

4. You may leave `GROQ_MODEL` blank. The application attempts to list your account's available models and select a text/chat model. If automatic selection does not work, set `GROQ_MODEL` to a currently supported model ID shown in your Groq account.

**Security:** Treat the API key like a password. Never share it, include it in screenshots, or upload `.env` to GitHub. `.gitignore` excludes it.

## Run the application

With the virtual environment activated, run:

```powershell
python app.py
```

The terminal prints the local address and attempts to open it in your default browser:

<http://127.0.0.1:5000>

If Chrome does not open automatically, open Chrome and enter that address manually. Keep the terminal open while using the application. Press `Ctrl+C` in the terminal to stop the server.

## How to use

### Add a student

Enter Student ID, Student Name, Class/Semester, comma-separated subject names and comma-separated marks in the same order. Example:

- Subjects: `Python, Mathematics, English, Database`
- Marks: `88, 76, 92, 81`

Click **Add**. Required fields, duplicate IDs/subjects, subject/mark counts and marks from 0 to 100 are validated.

### View and search

All saved records appear in the table. Search by student name or ID using the search box and **Search**. Click **Show All** to restore all records. Select a row to load its information into the form.

### Update or delete

Select a student row first. Edit the details and click **Update selected**. The Student ID is fixed and cannot be changed. Click **Delete selected** and confirm to remove the record.

### Results

The app calculates:

- Total = sum of subject marks
- Average percentage = total divided by the number of subjects
- Grade:
  - A: 85% or above
  - B: 70% to below 85%
  - C: 60% to below 70%
  - D: 50% to below 60%
  - F: below 50%

For the sample record, 88 + 76 + 92 + 81 = 337; 337 / 4 = 84.25%; grade B.

### AI features

Select a student, then click **Analyze Performance** for strong/weak subject analysis and improvement suggestions, or **Generate Study Tips** for a weekly plan, daily tips and practical recommendations. Wait for the response. Both features require internet access and a valid Groq API key/model.

## Data storage and backup

Records are stored in `students.json` in the project folder. The app reads this file on startup and saves changes after add/update/delete. Back up this file regularly. Do not delete it if you want to preserve your records.

## Common problems

| Problem | Solution |
|---|---|
| `can't open file ... main.py` | Run `python app.py`; the main file is `app.py`. |
| `No module named flask` | Activate `venv`, then run `python -m pip install -r requirements.txt`. |
| Template/page not found | Confirm the file is `templates/index.html`. |
| Browser link does not open | Keep Flask running and manually visit `http://127.0.0.1:5000`. |
| Address already in use | Stop another running app with `Ctrl+C`, then run again. |
| Groq API key not found | Ensure `.env` is in the project root and contains `GROQ_API_KEY=...`; restart the app. |
| Model unavailable | Set `GROQ_MODEL` to a currently supported text-generation model and restart. |
| Cannot reach AI service | Check internet access and Groq service/API status. Student record features remain available. |
| pip installation problem | Activate `venv` and run `python -m pip install -r requirements.txt`. |
| JSON file is damaged | Restore a backup of `students.json`. The app logs loading errors and starts with an empty list if the file cannot be read. |

## Learning notes

- `app.py` contains Flask routes, validation, result calculation and JSON storage.
- `ai_helper.py` contains Groq configuration and prompt functions.
- `templates/index.html` contains the page layout, styling and browser-side JavaScript.
- `students.json` is the local data file.

This is a local educational project using Flask's development server. It is intended for learning and classroom demonstration, not public production deployment.
