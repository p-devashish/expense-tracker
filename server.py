import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PORT = 8003
EXPENSES_FILE = 'expenses.json'

class ExpenseHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_file('index.html', 'text/html')
        elif self.path == '/expenses':
            self.get_expenses()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/expenses':
            self.add_expense()
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith('/expenses/'):
            self.update_expense()
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/expenses/'):
            self.delete_expense()
        else:
            self.send_error(404)

    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404)

    def get_expenses(self):
        expenses = self.load_expenses()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(expenses).encode())

    def add_expense(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            notes = data.get('notes', '').strip()
            amount = data.get('amount')
            dt_str = data.get('datetime')
            if not notes or amount is None or not dt_str:
                self.send_error(400, 'Invalid data')
                return
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
            self.send_response(201)
            self.end_headers()
        except Exception as e:
            print(f"Error in add_expense: {e}", file=sys.stderr)
            self.send_error(500, str(e))

    def update_expense(self):
        try:
            path_parts = self.path.split('/')
            if len(path_parts) != 3:
                self.send_error(400)
                return
            expense_id = int(path_parts[2])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data.decode())
            notes = data.get('notes', '').strip()
            amount = data.get('amount')
            dt_str = data.get('datetime')
            if not notes or amount is None or not dt_str:
                self.send_error(400, 'Invalid data')
                return
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            expenses = self.load_expenses()
            for exp in expenses:
                if exp['id'] == expense_id:
                    exp['notes'] = notes
                    exp['amount'] = float(amount)
                    exp['datetime'] = dt.isoformat()
                    break
            else:
                self.send_error(404, 'Expense not found')
                return
            self.save_expenses(expenses)
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            self.send_error(500, str(e))

    def delete_expense(self):
        try:
            path_parts = self.path.split('/')
            if len(path_parts) != 3:
                self.send_error(400)
                return
            expense_id = int(path_parts[2])
            expenses = self.load_expenses()
            expenses = [exp for exp in expenses if exp['id'] != expense_id]
            self.save_expenses(expenses)
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            self.send_error(500, str(e))

    def load_expenses(self):
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_expenses(self, expenses):
        with open(EXPENSES_FILE, 'w') as f:
            json.dump(expenses, f, indent=4)

if __name__ == '__main__':
    try:
        with socketserver.TCPServer(("", PORT), ExpenseHandler) as httpd:
            print(f"Serving at port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Server startup error: {e}")