"""
Mock Company Internal Application

A Flask web application simulating a company's internal systems including:
- Invoice management
- Employee directory
- Expense report tracking
- Task/ticket management

This provides both REST APIs and HTML pages for the AI agent to interact with.
"""
from __future__ import annotations

from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

import sqlite3
import json
import os


def create_app():
    """Application factory for the mock company app."""
    app = Flask(__name__)
    CORS(app)

    # Use a file-based SQLite database for reliability
    db_path = os.path.join(os.path.dirname(__file__), "company.db")

    def get_db():
        """Get a database connection."""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db():
        """Initialize the database with schema and seed data."""
        conn = get_db()
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                assignee_id INTEGER,
                status TEXT DEFAULT 'todo',
                FOREIGN KEY (assignee_id) REFERENCES employees(id)
            );
        """)

        # Seed only if empty
        if cursor.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0:
            from .seed_data import invoices, employees, expenses, tasks

            for inv in invoices:
                cursor.execute(
                    "INSERT INTO invoices (company, amount, due_date, status) VALUES (?, ?, ?, ?)",
                    (inv["company"], inv["amount"], inv["due_date"].isoformat(), inv["status"]),
                )
            for emp in employees:
                cursor.execute(
                    "INSERT INTO employees (name, department, role, email) VALUES (?, ?, ?, ?)",
                    (emp["name"], emp["department"], emp["role"], emp["email"]),
                )
            conn.commit()

            for exp in expenses:
                cursor.execute(
                    "INSERT INTO expenses (employee_id, amount, description, status) VALUES (?, ?, ?, ?)",
                    (exp["employee_id"], exp["amount"], exp["description"], exp["status"]),
                )
            for tsk in tasks:
                cursor.execute(
                    "INSERT INTO tasks (title, description, assignee_id, status) VALUES (?, ?, ?, ?)",
                    (tsk["title"], tsk["description"], tsk["assignee_id"], tsk["status"]),
                )
            conn.commit()

        conn.close()

    # Initialize database
    init_db()

    # ── Helper Functions ─────────────────────────────────────
    def row_to_dict(row):
        """Convert a sqlite3.Row to a dict."""
        if row is None:
            return None
        return dict(row)

    def rows_to_list(rows):
        """Convert a list of sqlite3.Row to list of dicts."""
        return [dict(r) for r in rows]

    # ── Error Handlers ───────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": str(e)}), 500

    # ── Invoice API ──────────────────────────────────────────
    @app.route("/api/invoices", methods=["GET"])
    def get_invoices():
        conn = get_db()
        query = "SELECT * FROM invoices WHERE 1=1"
        params = []

        if "company" in request.args:
            query += " AND company LIKE ?"
            params.append(f"%{request.args['company']}%")
        if "status" in request.args:
            query += " AND status = ?"
            params.append(request.args["status"])

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route("/api/invoices/<int:id>", methods=["GET"])
    def get_invoice(id):
        conn = get_db()
        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(row_to_dict(row))

    @app.route("/api/invoices", methods=["POST"])
    def create_invoice():
        data = request.json
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO invoices (company, amount, due_date, status) VALUES (?, ?, ?, ?)",
            (data["company"], data["amount"], data["due_date"], data.get("status", "pending")),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(row)), 201

    @app.route("/api/invoices/<int:id>", methods=["PUT"])
    def update_invoice(id):
        data = request.json
        conn = get_db()
        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Invoice not found"}), 404

        updates = []
        params = []
        for field in ["company", "amount", "due_date", "status"]:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])

        if updates:
            params.append(id)
            conn.execute(f"UPDATE invoices SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(row))

    @app.route("/api/invoices/<int:id>", methods=["DELETE"])
    def delete_invoice(id):
        conn = get_db()
        conn.execute("DELETE FROM invoices WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return "", 204

    # ── Employee API ─────────────────────────────────────────
    @app.route("/api/employees", methods=["GET"])
    def get_employees():
        conn = get_db()
        query = "SELECT * FROM employees WHERE 1=1"
        params = []

        if "department" in request.args:
            query += " AND department = ?"
            params.append(request.args["department"])
        if "name" in request.args:
            query += " AND name LIKE ?"
            params.append(f"%{request.args['name']}%")

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route("/api/employees/<int:id>", methods=["GET"])
    def get_employee(id):
        conn = get_db()
        row = conn.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Employee not found"}), 404
        return jsonify(row_to_dict(row))

    @app.route("/api/employees", methods=["POST"])
    def add_employee():
        data = request.json
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO employees (name, department, role, email) VALUES (?, ?, ?, ?)",
            (data["name"], data["department"], data["role"], data["email"]),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM employees WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(row)), 201

    @app.route("/api/employees/<int:id>", methods=["PUT"])
    def update_employee(id):
        data = request.json
        conn = get_db()
        updates = []
        params = []
        for field in ["name", "department", "role", "email"]:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])

        if updates:
            params.append(id)
            conn.execute(f"UPDATE employees SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

        row = conn.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Employee not found"}), 404
        return jsonify(row_to_dict(row))

    # ── Expense API ──────────────────────────────────────────
    @app.route("/api/expenses", methods=["GET"])
    def get_expenses():
        conn = get_db()
        query = """
            SELECT e.*, emp.name as employee_name 
            FROM expenses e 
            LEFT JOIN employees emp ON e.employee_id = emp.id 
            WHERE 1=1
        """
        params = []

        if "employee_id" in request.args:
            query += " AND e.employee_id = ?"
            params.append(request.args["employee_id"])
        if "status" in request.args:
            query += " AND e.status = ?"
            params.append(request.args["status"])

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route("/api/expenses", methods=["POST"])
    def submit_expense():
        data = request.json
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO expenses (employee_id, amount, description, status) VALUES (?, ?, ?, ?)",
            (data["employee_id"], data["amount"], data["description"], data.get("status", "pending")),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(row)), 201

    @app.route("/api/expenses/<int:id>/approve", methods=["PUT"])
    def approve_expense(id):
        conn = get_db()
        conn.execute("UPDATE expenses SET status = 'approved' WHERE id = ?", (id,))
        conn.commit()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(row_to_dict(row))

    @app.route("/api/expenses/<int:id>/reject", methods=["PUT"])
    def reject_expense(id):
        conn = get_db()
        conn.execute("UPDATE expenses SET status = 'rejected' WHERE id = ?", (id,))
        conn.commit()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(row_to_dict(row))

    # ── Task API ─────────────────────────────────────────────
    @app.route("/api/tasks", methods=["GET"])
    def get_tasks():
        conn = get_db()
        query = """
            SELECT t.*, emp.name as assignee_name 
            FROM tasks t 
            LEFT JOIN employees emp ON t.assignee_id = emp.id 
            WHERE 1=1
        """
        params = []

        if "status" in request.args:
            query += " AND t.status = ?"
            params.append(request.args["status"])
        if "assignee" in request.args:
            query += " AND t.assignee_id = ?"
            params.append(request.args["assignee"])

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        data = request.json
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, assignee_id, status) VALUES (?, ?, ?, ?)",
            (data["title"], data.get("description"), data.get("assignee_id"), data.get("status", "todo")),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        return jsonify(row_to_dict(row)), 201

    @app.route("/api/tasks/<int:id>", methods=["PUT"])
    def update_task(id):
        data = request.json
        conn = get_db()
        updates = []
        params = []
        for field in ["title", "description", "assignee_id", "status"]:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])

        if updates:
            params.append(id)
            conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(row_to_dict(row))

    @app.route("/api/tasks/<int:id>/complete", methods=["PUT"])
    def complete_task(id):
        conn = get_db()
        conn.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (id,))
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(row_to_dict(row))

    # ── System/Meta API ──────────────────────────────────────
    @app.route("/api/status", methods=["GET"])
    def get_status():
        return jsonify({"status": "ok", "version": "1.0.0", "name": "Company Internal System"})

    @app.route("/api/search", methods=["GET"])
    def global_search():
        q = request.args.get("q", "")
        results = {"invoices": [], "employees": [], "expenses": [], "tasks": []}
        if q:
            conn = get_db()
            results["invoices"] = rows_to_list(
                conn.execute("SELECT * FROM invoices WHERE company LIKE ?", (f"%{q}%",)).fetchall()
            )
            results["employees"] = rows_to_list(
                conn.execute("SELECT * FROM employees WHERE name LIKE ? OR department LIKE ?", (f"%{q}%", f"%{q}%")).fetchall()
            )
            results["tasks"] = rows_to_list(
                conn.execute("SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?", (f"%{q}%", f"%{q}%")).fetchall()
            )
            results["expenses"] = rows_to_list(
                conn.execute("SELECT * FROM expenses WHERE description LIKE ?", (f"%{q}%",)).fetchall()
            )
            conn.close()
        return jsonify(results)

    # ── HTML Frontend ────────────────────────────────────────
    BASE_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Company Internal System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding-top: 1rem; background-color: #f8f9fa; }
            .card { box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: none; border-radius: 10px; }
            .sidebar { background: linear-gradient(135deg, #2c3e50, #34495e); min-height: calc(100vh - 3rem); border-radius: 10px; padding: 1.5rem 1rem; }
            .sidebar a { color: #ecf0f1; text-decoration: none; display: block; padding: 10px 15px; border-radius: 6px; margin-bottom: 4px; transition: background 0.2s; }
            .sidebar a:hover, .sidebar a.active { background-color: rgba(255,255,255,0.15); }
            .stat-card { transition: transform 0.2s; }
            .stat-card:hover { transform: translateY(-3px); }
            h2 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <div class="container-fluid px-4">
            <header class="d-flex align-items-center pb-2 mb-3 border-bottom">
                <span class="fs-4 fw-bold text-primary">🏢 Company Internal Portal</span>
            </header>
            <div class="row">
                <div class="col-md-2">
                    <div class="sidebar">
                        <a href="/">📊 Dashboard</a>
                        <a href="/invoices">📄 Invoices</a>
                        <a href="/employees">👥 Employees</a>
                        <a href="/expenses">💰 Expenses</a>
                        <a href="/tasks">✅ Tasks</a>
                    </div>
                </div>
                <div class="col-md-10">
                    {{ content | safe }}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    @app.route("/")
    def dashboard():
        conn = get_db()
        invoice_count = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        employee_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        pending_expenses = conn.execute("SELECT COUNT(*) FROM expenses WHERE status='pending'").fetchone()[0]
        open_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status != 'done'").fetchone()[0]
        overdue_invoices = conn.execute("SELECT COUNT(*) FROM invoices WHERE status='overdue'").fetchone()[0]
        total_pending = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE status='pending'").fetchone()[0]
        conn.close()

        content = f"""
        <h2 class="mb-4">📊 Dashboard</h2>
        <div class="row g-3">
            <div class="col-md-4"><div class="card p-4 stat-card bg-primary text-white"><h5>Total Invoices</h5><h2>{invoice_count}</h2></div></div>
            <div class="col-md-4"><div class="card p-4 stat-card bg-success text-white"><h5>Total Employees</h5><h2>{employee_count}</h2></div></div>
            <div class="col-md-4"><div class="card p-4 stat-card bg-warning text-dark"><h5>Pending Expenses</h5><h2>{pending_expenses}</h2></div></div>
            <div class="col-md-4"><div class="card p-4 stat-card bg-info text-white"><h5>Open Tasks</h5><h2>{open_tasks}</h2></div></div>
            <div class="col-md-4"><div class="card p-4 stat-card bg-danger text-white"><h5>Overdue Invoices</h5><h2>{overdue_invoices}</h2></div></div>
            <div class="col-md-4"><div class="card p-4 stat-card bg-secondary text-white"><h5>Pending Amount</h5><h2>${total_pending:,.2f}</h2></div></div>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    @app.route("/invoices")
    def invoices_page():
        conn = get_db()
        invoices = rows_to_list(conn.execute("SELECT * FROM invoices ORDER BY id").fetchall())
        conn.close()

        rows_html = ""
        for inv in invoices:
            status_badge = {"paid": "success", "pending": "warning", "overdue": "danger"}.get(inv["status"], "secondary")
            rows_html += f"""
            <tr>
                <td>{inv['id']}</td>
                <td>{inv['company']}</td>
                <td>${inv['amount']:,.2f}</td>
                <td>{inv['due_date']}</td>
                <td><span class="badge bg-{status_badge}">{inv['status']}</span></td>
                <td><a href="/invoices/{inv['id']}" class="btn btn-sm btn-outline-primary">View</a></td>
            </tr>
            """

        content = f"""
        <h2 class="mb-4">📄 Invoices</h2>
        <div class="card p-3">
            <table class="table table-hover">
                <thead><tr><th>ID</th><th>Company</th><th>Amount</th><th>Due Date</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    @app.route("/invoices/<int:id>")
    def invoice_detail_page(id):
        conn = get_db()
        inv = row_to_dict(conn.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone())
        conn.close()
        if not inv:
            return "Invoice not found", 404

        content = f"""
        <h2 class="mb-4">📄 Invoice #{inv['id']}</h2>
        <div class="card p-4">
            <p><strong>Company:</strong> {inv['company']}</p>
            <p><strong>Amount:</strong> ${inv['amount']:,.2f}</p>
            <p><strong>Due Date:</strong> {inv['due_date']}</p>
            <p><strong>Status:</strong> {inv['status']}</p>
            <a href="/invoices" class="btn btn-secondary mt-3">← Back to Invoices</a>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    @app.route("/employees")
    def employees_page():
        conn = get_db()
        employees = rows_to_list(conn.execute("SELECT * FROM employees ORDER BY id").fetchall())
        conn.close()

        rows_html = ""
        for emp in employees:
            rows_html += f"<tr><td>{emp['id']}</td><td>{emp['name']}</td><td>{emp['department']}</td><td>{emp['role']}</td><td>{emp['email']}</td></tr>"

        content = f"""
        <h2 class="mb-4">👥 Employees</h2>
        <div class="card p-3">
            <table class="table table-hover">
                <thead><tr><th>ID</th><th>Name</th><th>Department</th><th>Role</th><th>Email</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    @app.route("/expenses")
    def expenses_page():
        conn = get_db()
        expenses = rows_to_list(conn.execute(
            "SELECT e.*, emp.name as employee_name FROM expenses e LEFT JOIN employees emp ON e.employee_id = emp.id ORDER BY e.id"
        ).fetchall())
        conn.close()

        rows_html = ""
        for exp in expenses:
            status_badge = {"approved": "success", "pending": "warning", "rejected": "danger"}.get(exp["status"], "secondary")
            rows_html += f"""
            <tr>
                <td>{exp['id']}</td>
                <td>{exp.get('employee_name', 'N/A')}</td>
                <td>${exp['amount']:,.2f}</td>
                <td>{exp['description']}</td>
                <td><span class="badge bg-{status_badge}">{exp['status']}</span></td>
            </tr>
            """

        content = f"""
        <h2 class="mb-4">💰 Expense Reports</h2>
        <div class="card p-3">
            <table class="table table-hover">
                <thead><tr><th>ID</th><th>Employee</th><th>Amount</th><th>Description</th><th>Status</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    @app.route("/tasks")
    def tasks_page():
        conn = get_db()
        tasks = rows_to_list(conn.execute(
            "SELECT t.*, emp.name as assignee_name FROM tasks t LEFT JOIN employees emp ON t.assignee_id = emp.id ORDER BY t.id"
        ).fetchall())
        conn.close()

        rows_html = ""
        for tsk in tasks:
            status_badge = {"done": "success", "in_progress": "info", "todo": "secondary"}.get(tsk["status"], "secondary")
            rows_html += f"""
            <tr>
                <td>{tsk['id']}</td>
                <td>{tsk['title']}</td>
                <td>{tsk.get('assignee_name', 'Unassigned')}</td>
                <td><span class="badge bg-{status_badge}">{tsk['status']}</span></td>
            </tr>
            """

        content = f"""
        <h2 class="mb-4">✅ Tasks</h2>
        <div class="card p-3">
            <table class="table table-hover">
                <thead><tr><th>ID</th><th>Title</th><th>Assignee</th><th>Status</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """
        return render_template_string(BASE_HTML, content=content)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
