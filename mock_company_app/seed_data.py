from datetime import date, timedelta
import random

# Seed Data
invoices = [
    {'company': 'Acme Corp', 'amount': 1500.00, 'due_date': date.today() - timedelta(days=5), 'status': 'overdue'},
    {'company': 'TechFlow Solutions', 'amount': 3200.50, 'due_date': date.today() + timedelta(days=10), 'status': 'pending'},
    {'company': 'Global Dynamics', 'amount': 10500.00, 'due_date': date.today() - timedelta(days=2), 'status': 'paid'},
    {'company': 'Stark Industries', 'amount': 999.99, 'due_date': date.today() + timedelta(days=30), 'status': 'pending'},
    {'company': 'Wayne Enterprises', 'amount': 5000.00, 'due_date': date.today() - timedelta(days=15), 'status': 'overdue'},
    {'company': 'Acme Corp', 'amount': 450.00, 'due_date': date.today() + timedelta(days=5), 'status': 'pending'},
    {'company': 'Umbrella Corp', 'amount': 8750.25, 'due_date': date.today() - timedelta(days=20), 'status': 'paid'},
    {'company': 'Cyberdyne Systems', 'amount': 12000.00, 'due_date': date.today() + timedelta(days=45), 'status': 'pending'},
    {'company': 'Initech', 'amount': 300.00, 'due_date': date.today() - timedelta(days=1), 'status': 'overdue'},
]

employees = [
    {'name': 'Alice Smith', 'department': 'Engineering', 'role': 'Senior Developer', 'email': 'alice@example.com'},
    {'name': 'Bob Johnson', 'department': 'Sales', 'role': 'Sales Representative', 'email': 'bob@example.com'},
    {'name': 'Charlie Davis', 'department': 'HR', 'role': 'HR Manager', 'email': 'charlie@example.com'},
    {'name': 'Diana Prince', 'department': 'Marketing', 'role': 'Marketing Director', 'email': 'diana@example.com'},
    {'name': 'Eve Adams', 'department': 'Engineering', 'role': 'QA Engineer', 'email': 'eve@example.com'},
    {'name': 'Frank Castle', 'department': 'Security', 'role': 'Security Officer', 'email': 'frank@example.com'},
    {'name': 'Grace Hopper', 'department': 'Engineering', 'role': 'Lead Architect', 'email': 'grace@example.com'},
    {'name': 'Hank Pym', 'department': 'R&D', 'role': 'Chief Scientist', 'email': 'hank@example.com'},
]

expenses = [
    {'employee_id': 1, 'amount': 150.00, 'description': 'Monthly cloud hosting', 'status': 'approved'},
    {'employee_id': 2, 'amount': 345.50, 'description': 'Client dinner at Steakhouse', 'status': 'pending'},
    {'employee_id': 4, 'amount': 1200.00, 'description': 'Digital ad campaign', 'status': 'approved'},
    {'employee_id': 6, 'amount': 55.00, 'description': 'Flashlights', 'status': 'rejected'},
    {'employee_id': 8, 'amount': 5000.00, 'description': 'Lab equipment', 'status': 'pending'},
]

tasks = [
    {'title': 'Fix login bug', 'description': 'Users cannot login with SSO', 'assignee_id': 1, 'status': 'in_progress'},
    {'title': 'Quarterly Report', 'description': 'Prepare Q3 sales report', 'assignee_id': 2, 'status': 'todo'},
    {'title': 'Update Employee Handbook', 'description': 'Add new remote work policy', 'assignee_id': 3, 'status': 'done'},
    {'title': 'Deploy new landing page', 'description': 'Launch the Halloween campaign', 'assignee_id': 4, 'status': 'in_progress'},
    {'title': 'Run security audit', 'description': 'Check for vulnerabilities in the main app', 'assignee_id': 6, 'status': 'todo'},
    {'title': 'Optimize database queries', 'description': 'Speed up the invoice dashboard', 'assignee_id': 7, 'status': 'todo'},
]
