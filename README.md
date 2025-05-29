# Workout Tracker

A comprehensive web application for tracking workouts, managing exercise routines, and monitoring fitness progress. Built with Flask and modern web technologies.

## Features

- **Exercise Management**
  - Create and customize exercises
  - Categorize exercises by type (strength, cardio, etc.)
  - Track personal records and progress
  - Add detailed exercise instructions and notes

- **Workout Plans**
  - Create custom workout plans
  - Save plans as templates for reuse
  - Track active workout plans
  - Monitor plan progress and completion

- **Workout Logging**
  - Log individual workout sessions
  - Track sets, reps, weights, and duration
  - Record personal records and achievements
  - Add notes and observations

- **Progress Tracking**
  - Visual progress charts and graphs
  - Track personal records
  - Monitor workout frequency
  - Analyze exercise distribution

- **User Dashboard**
  - Overview of recent workouts
  - Quick access to active plans
  - Personal records display
  - Workout statistics

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLAlchemy, SQLite
- **UI Framework**: Bootstrap 5
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Charts**: Chart.js

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- virtualenv (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/michaelbZA/workout_tracker.git
   cd workout_tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create a .env file in the project root
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

The application will be available at `http://localhost:5000`

## Project Structure

```
workout_tracker/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── migrations/
├── tests/
├── venv/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Bootstrap for the UI framework
- Chart.js for data visualization
- Flask community for the excellent web framework

## Contact

Michael Brunger - [Email Me](mailto:michaelbrunger@gmail.com)
Project Link: [https://github.com/michaelbZA/workout_tracker](https://github.com/michaelbZA/workout_tracker) 