# Event Management System using DSA

Flask + MySQL college mini project. User registration/login, event submission, admin approval/rejection, and four DSA phase pages.

## DSA phases
1. **Linked List** — manually implemented singly linked list to insert/traverse/delete event records.
2. **Binary Search Tree** — manually implemented BST keyed by Event ID for search.
3. **Merge Sort** — manually implemented merge sort to sort approved events by date.
4. **Graph + BFS** — venue adjacency-list graph and breadth-first traversal.

## Setup (VS Code)
1. Install Python 3.10+ and MySQL Server.
2. Open this folder in VS Code and create/activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. In MySQL Workbench, open and execute `database.sql`.
5. Copy `.env.example` to `.env`, set your MySQL password and a strong Flask secret key.
6. Set environment variables in your terminal (PowerShell example):
   `$env:DB_PASSWORD='your_mysql_password'; $env:FLASK_SECRET_KEY='replace-with-secret'`
   Also set DB_HOST, DB_USER, DB_NAME if they differ from defaults.
7. Run `python app.py`.
8. Open `http://127.0.0.1:5000/setup-admin` once to create the first admin. **Remove/disable this route after creating the admin before deployment.**
9. User registration: `/register`; user login: `/login`; admin login: `/admin/login`.

## Important
- Events submitted by users start as `Pending`; only admins can approve/reject. Only approved events are shown in public event listings.
- Never commit real passwords or secret keys. The included setup route is intended for local development only.
- For production, disable Flask debug mode, configure CSRF protection, HTTPS, and secure session cookies.
