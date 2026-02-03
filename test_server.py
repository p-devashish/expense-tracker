import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

# Copy the logic from server.py to a testable class
class TestableExpenseHandler:
    EXPENSES_FILE = 'expenses.json'

    def load_expenses(self):
        if os.path.exists(self.EXPENSES_FILE):
            with open(self.EXPENSES_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_expenses(self, expenses):
        with open(self.EXPENSES_FILE, 'w') as f:
            json.dump(expenses, f, indent=4)

    def add_expense_logic(self, data):
        from datetime import datetime
        notes = data.get('notes', '').strip()
        amount = data.get('amount')
        dt_str = data.get('datetime')
        if not notes or amount is None or not dt_str:
            raise ValueError('Invalid data')
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        expenses = self.load_expenses()
        expense_id = max([e['id'] for e in expenses], default=0) + 1
        expense = {
            'id': expense_id,
            'notes': notes,
            'amount': float(amount),
            'datetime': dt.isoformat()
        }
        expenses.append(expense)
        self.save_expenses(expenses)
        return expense

    def update_expense_logic(self, expense_id, data):
        from datetime import datetime
        notes = data.get('notes', '').strip()
        amount = data.get('amount')
        dt_str = data.get('datetime')
        if not notes or amount is None or not dt_str:
            raise ValueError('Invalid data')
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        expenses = self.load_expenses()
        for exp in expenses:
            if exp['id'] == expense_id:
                exp['notes'] = notes
                exp['amount'] = float(amount)
                exp['datetime'] = dt.isoformat()
                break
        else:
            raise ValueError('Expense not found')
        self.save_expenses(expenses)

    def delete_expense_logic(self, expense_id):
        expenses = self.load_expenses()
        expenses = [exp for exp in expenses if exp['id'] != expense_id]
        self.save_expenses(expenses)

class TestExpenseHandler(unittest.TestCase):
    def setUp(self):
        self.handler = TestableExpenseHandler()
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        self.temp_file.close()
        self.handler.EXPENSES_FILE = self.temp_file.name
        # Initialize empty expenses
        with open(self.handler.EXPENSES_FILE, 'w') as f:
            json.dump([], f)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_expenses_empty(self):
        expenses = self.handler.load_expenses()
        self.assertEqual(expenses, [])

    def test_save_and_load_expenses(self):
        expenses = [{'id': 1, 'notes': 'test', 'amount': 100.0, 'datetime': '2023-01-01T00:00:00'}]
        self.handler.save_expenses(expenses)
        loaded = self.handler.load_expenses()
        self.assertEqual(loaded, expenses)

    def test_add_expense_success(self):
        data = {"notes": "new expense", "amount": 150.0, "datetime": "2023-01-01T00:00:00"}
        expense = self.handler.add_expense_logic(data)
        self.assertEqual(expense['notes'], 'new expense')
        self.assertEqual(expense['amount'], 150.0)
        expenses = self.handler.load_expenses()
        self.assertEqual(len(expenses), 1)

    def test_add_expense_invalid_data(self):
        data = {"notes": "", "amount": 0}
        with self.assertRaises(ValueError):
            self.handler.add_expense_logic(data)

    def test_update_expense_success(self):
        # Add an expense first
        self.handler.save_expenses([{'id': 1, 'notes': 'old', 'amount': 100.0, 'datetime': '2023-01-01T00:00:00'}])
        data = {"notes": "updated", "amount": 200.0, "datetime": "2023-01-01T00:00:00"}
        self.handler.update_expense_logic(1, data)
        loaded = self.handler.load_expenses()
        self.assertEqual(loaded[0]['notes'], 'updated')
        self.assertEqual(loaded[0]['amount'], 200.0)

    def test_update_expense_not_found(self):
        data = {"notes": "updated", "amount": 200.0, "datetime": "2023-01-01T00:00:00"}
        with self.assertRaises(ValueError):
            self.handler.update_expense_logic(999, data)

    def test_delete_expense_success(self):
        self.handler.save_expenses([{'id': 1, 'notes': 'test', 'amount': 100.0, 'datetime': '2023-01-01T00:00:00'}])
        self.handler.delete_expense_logic(1)
        loaded = self.handler.load_expenses()
        self.assertEqual(loaded, [])

    def test_delete_expense_invalid_id(self):
        # Deleting non-existent is fine, just does nothing
        self.handler.delete_expense_logic(999)
        # No error, just empty
        loaded = self.handler.load_expenses()
        self.assertEqual(loaded, [])

    def test_get_expenses(self):
        expenses = [{'id': 1, 'notes': 'test', 'amount': 100.0, 'datetime': '2023-01-01T00:00:00'}]
        self.handler.save_expenses(expenses)
        loaded = self.handler.load_expenses()
        self.assertEqual(loaded, expenses)

if __name__ == '__main__':
    unittest.main()