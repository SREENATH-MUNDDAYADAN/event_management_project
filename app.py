from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
from linked_list import EventLinkedList
from binary_search_tree import EventBST
from merge_sort import merge_sort
from graph_bfs import VenueGraph

app=Flask(__name__)
app.secret_key=os.getenv('FLASK_SECRET_KEY','dev-only-change-me')

# All SQL uses parameters. Database schema is provided in database.sql.
def db_rows(sql, params=()):
    conn=get_connection(); cur=conn.cursor(dictionary=True)
    try: cur.execute(sql,params); return cur.fetchall()
    finally: cur.close(); conn.close()
def db_exec(sql, params=()):
    conn=get_connection(); cur=conn.cursor()
    try: cur.execute(sql,params); conn.commit(); return cur.lastrowid
    except Exception: conn.rollback(); raise
    finally: cur.close(); conn.close()
def user_required(fn):
    @wraps(fn)
    def wrap(*a,**kw):
        if session.get('role')!='user': flash('Please sign in as a user.','warning'); return redirect(url_for('user_login'))
        return fn(*a,**kw)
    return wrap
def admin_required(fn):
    @wraps(fn)
    def wrap(*a,**kw):
        if session.get('role')!='admin': flash('Administrator login required.','warning'); return redirect(url_for('admin_login'))
        return fn(*a,**kw)
    return wrap
def all_events(): return db_rows('SELECT e.*, u.full_name AS submitter FROM events e JOIN users u ON u.user_id=e.user_id ORDER BY e.event_id DESC')
def linked_events(events):
    ll=EventLinkedList()
    for e in events: ll.insert(e)
    return ll.to_list()
def event_bst(events):
    tree=EventBST()
    for e in events: tree.insert(e)
    return tree

@app.route('/')
def index():
    if session.get('role')=='admin': return redirect(url_for('admin_dashboard'))
    if session.get('role')=='user': return redirect(url_for('user_dashboard'))
    return redirect(url_for('user_login'))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('full_name','').strip(); email=request.form.get('email','').strip().lower(); phone=request.form.get('phone','').strip(); pw=request.form.get('password',''); confirm=request.form.get('confirm_password','')
        if not name or not email or not pw: flash('Please complete all required fields.','danger')
        elif pw!=confirm: flash('Passwords do not match.','danger')
        elif len(pw)<8: flash('Password must contain at least 8 characters.','danger')
        else:
            try: db_exec('INSERT INTO users(full_name,email,phone,password_hash) VALUES(%s,%s,%s,%s)',(name,email,phone,generate_password_hash(pw))); flash('Registration successful. Please log in.','success'); return redirect(url_for('user_login'))
            except Exception: flash('That email may already be registered.','danger')
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        rows=db_rows('SELECT * FROM users WHERE email=%s',(email,))
        if rows and check_password_hash(rows[0]['password_hash'],pw):
            session.clear(); session.update(role='user',user_id=rows[0]['user_id'],name=rows[0]['full_name']); return redirect(url_for('user_dashboard'))
        flash('Invalid email or password.','danger')
    return render_template('login.html',admin=False)
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        rows=db_rows('SELECT * FROM admins WHERE email=%s',(email,))
        if rows and check_password_hash(rows[0]['password_hash'],pw):
            session.clear(); session.update(role='admin',admin_id=rows[0]['admin_id'],name=rows[0]['admin_name']); return redirect(url_for('admin_dashboard'))
        flash('Invalid administrator credentials.','danger')
    return render_template('login.html',admin=True)
@app.route('/logout')
def logout(): session.clear(); flash('You have logged out.','info'); return redirect(url_for('user_login'))

@app.route('/dashboard')
@user_required
def user_dashboard():
    ev=db_rows('SELECT * FROM events WHERE user_id=%s ORDER BY event_id DESC',(session['user_id'],))
    stats={'total':len(ev),'pending':sum(x['status']=='Pending' for x in ev),'approved':sum(x['status']=='Approved' for x in ev),'rejected':sum(x['status']=='Rejected' for x in ev)}
    approved=db_rows("SELECT * FROM events WHERE status='Approved' AND event_date>=CURDATE() ORDER BY event_date LIMIT 4")
    return render_template('dashboard.html',stats=stats,events=approved,admin=False)
@app.route('/admin')
@admin_required
def admin_dashboard():
    ev=all_events(); stats={'total':len(ev),'pending':sum(x['status']=='Pending' for x in ev),'approved':sum(x['status']=='Approved' for x in ev),'rejected':sum(x['status']=='Rejected' for x in ev),'users':len(db_rows('SELECT user_id FROM users'))}
    return render_template('dashboard.html',stats=stats,events=[e for e in ev if e['status']=='Approved'][:4],admin=True)

@app.route('/events')
@user_required
def events(): return render_template('events.html',events=db_rows("SELECT * FROM events WHERE status='Approved' ORDER BY event_date"),admin=False)
@app.route('/my-events')
@user_required
def my_events(): return render_template('events.html',events=db_rows('SELECT * FROM events WHERE user_id=%s ORDER BY event_id DESC',(session['user_id'],)),admin=False,mine=True)
@app.route('/add-event',methods=['GET','POST'])
@user_required
def add_event():
    if request.method=='POST':
        f=request.form
        try:
            name=f.get('event_name','').strip(); category=f.get('category','').strip(); date=f.get('event_date',''); venue=f.get('venue','').strip(); participants=int(f.get('expected_participants') or 0)
            if not all([name,category,date,venue]): raise ValueError()
            db_exec('INSERT INTO events(user_id,event_name,category,description,event_date,event_time,venue,organizer_name,contact_number,expected_participants,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(session['user_id'],name,category,f.get('description',''),date,f.get('event_time') or None,venue,f.get('organizer_name',''),f.get('contact_number',''),participants,'Pending'))
            flash('Event submitted. It will appear publicly after admin approval.','success'); return redirect(url_for('my_events'))
        except Exception: flash('Please check the form values and try again.','danger')
    return render_template('add_event.html')
@app.route('/admin/events')
@admin_required
def admin_events(): return render_template('events.html',events=all_events(),admin=True)
@app.route('/admin/pending')
@admin_required
def pending_events(): return render_template('events.html',events=db_rows("SELECT e.*,u.full_name AS submitter FROM events e JOIN users u ON u.user_id=e.user_id WHERE e.status='Pending' ORDER BY e.submitted_at"),admin=True,pending=True)
@app.route('/admin/event/<int:event_id>/<action>',methods=['POST'])
@admin_required
def event_action(event_id,action):
    if action=='approve': db_exec("UPDATE events SET status='Approved',approved_by=%s,approval_date=NOW(),rejection_reason=NULL WHERE event_id=%s AND status='Pending'",(session['admin_id'],event_id)); flash('Event approved.','success')
    elif action=='reject': db_exec("UPDATE events SET status='Rejected',approved_by=%s,approval_date=NOW(),rejection_reason=%s WHERE event_id=%s AND status='Pending'",(session['admin_id'],request.form.get('reason','Rejected by admin'),event_id)); flash('Event rejected.','info')
    else: flash('Invalid action.','danger')
    return redirect(request.referrer or url_for('pending_events'))
@app.route('/admin/users')
@admin_required
def users(): return render_template('users.html',users=db_rows('SELECT user_id,full_name,email,phone,created_at FROM users ORDER BY user_id DESC'))

# DSA phase pages: each uses its own manually implemented technique.
@app.route('/phase/linked-list')
@user_required
def phase_linked(): return render_template('phase.html',phase=1,title='Linked List',description='Manage event records by traversing a manually implemented singly linked list.',items=linked_events(db_rows('SELECT * FROM events WHERE user_id=%s ORDER BY event_id DESC',(session['user_id'],))))
@app.route('/phase/bst',methods=['GET','POST'])
@user_required
def phase_bst():
    tree=event_bst(db_rows('SELECT * FROM events WHERE user_id=%s',(session['user_id'],))); found=None; key=request.form.get('event_id','').strip() if request.method=='POST' else ''
    if key:
        if key.isdigit(): found=tree.search(int(key))
        else: flash('Event ID must be numeric.','warning')
        if not found: flash('Event not found.','info')
    return render_template('phase.html',phase=2,title='Binary Search Tree',description='Search event records by Event ID using a manually implemented BST.',items=tree.inorder(),found=found,key=key)
@app.route('/phase/merge-sort')
@user_required
def phase_sort():
    items=db_rows("SELECT * FROM events WHERE user_id=%s AND status='Approved'",(session['user_id'],)); return render_template('phase.html',phase=3,title='Merge Sort',description='Approved events sorted chronologically using manual merge sort.',items=merge_sort(items))
@app.route('/phase/graph',methods=['GET','POST'])
@user_required
def phase_graph():
    venues=db_rows('SELECT venue_name FROM venues ORDER BY venue_name'); edges=db_rows('SELECT a.venue_name AS a,b.venue_name AS b FROM venue_edges e JOIN venues a ON a.venue_id=e.venue_from JOIN venues b ON b.venue_id=e.venue_to'); graph=VenueGraph()
    for v in venues: graph.add_vertex(v['venue_name'])
    for e in edges: graph.add_edge(e['a'],e['b'])
    start=request.form.get('start',''); traversal=graph.bfs(start) if start else []
    return render_template('phase.html',phase=4,title='Graph Traversal using BFS',description='Explore connected event venues using a graph adjacency list and breadth-first search.',items=venues,traversal=traversal,start=start,edges=edges)
@app.route('/admin/venues',methods=['GET','POST'])
@admin_required
def venue_admin():
    if request.method=='POST':
        a=request.form.get('venue_a','').strip(); b=request.form.get('venue_b','').strip()
        if a and b and a!=b:
            for name in (a,b):
                try: db_exec('INSERT INTO venues(venue_name) VALUES(%s)',(name,))
                except Exception: pass
            ids=db_rows('SELECT venue_id,venue_name FROM venues WHERE venue_name IN (%s,%s)',(a,b)); mapping={x['venue_name']:x['venue_id'] for x in ids}
            if a in mapping and b in mapping:
                try: db_exec('INSERT INTO venue_edges(venue_from,venue_to) VALUES(%s,%s)',(mapping[a],mapping[b])); flash('Venue connection added.','success')
                except Exception: flash('Connection already exists.','info')
    return render_template('venue_admin.html',venues=db_rows('SELECT * FROM venues ORDER BY venue_name'))
@app.route('/setup-admin',methods=['GET','POST'])
def setup_admin():
    # One-time bootstrap: set a strong password and then remove this route before deployment.
    if db_rows('SELECT admin_id FROM admins LIMIT 1'): return 'Admin already exists. Remove this setup route before deployment.',403
    if request.method=='POST':
        name=request.form.get('name','Administrator').strip(); email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        if email and len(pw)>=8:
            db_exec('INSERT INTO admins(admin_name,email,password_hash) VALUES(%s,%s,%s)',(name,email,generate_password_hash(pw))); return redirect(url_for('admin_login'))
        flash('Enter email and a password of at least 8 characters.','danger')
    return render_template('setup_admin.html')

if __name__=='__main__': app.run(debug=True)
