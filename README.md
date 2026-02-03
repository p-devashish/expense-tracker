# Expenso

A simple expense tracker web app with a backend API.

## Features

- Add expenses with notes, amount in rupees (₹), and date/time (defaults to current time).
- Edit and delete expenses via a menu (three dots) on each expense card.
- Edit expenses in a modal popup with all fields editable.
- View a list of added expenses grouped by month-year in card format.
- Backend API for storing expenses (persisted to `expenses.json`).
- Dark brown theme with lighter text shades.
- Money icon logo with stylish Poppins font.
- Placeholder text when no expenses are added.
- Add Expense button positioned at the bottom.
- Visual notifications for add, update, and delete actions (bottom-right popup with progress bar).
- Designed for future web and mobile versions.

## How to Run

1. Ensure Python 3 is installed.
2. Run the server: `python3 server.py`
3. Open a web browser and go to `http://localhost:8003`
4. Fill in the notes, amount (in ₹), and optionally adjust the date/time.
5. Click "Add Expense" to add it to the list.
6. Expenses are grouped under month-year headings.

## Running Tests

Run the unit tests: `python3 -m unittest test_server.py`

The tests cover the core functionalities (add, edit, delete, get expenses) with high coverage.

## Files

- `server.py`: Python backend server using `http.server`.
- `index.html`: Frontend web application.
- `test_server.py`: Unit tests for the backend logic.
- `expenses.json`: Data file for storing expenses (created automatically).
