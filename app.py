from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secure-random-key'
DB_DIR = 'database'
DB_PATH = os.path.join(DB_DIR, 'feedback.db')

# Ensure database folder exists
os.makedirs(DB_DIR, exist_ok=True)

# Initialize database if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        room_number TEXT,
        meal_type TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        date_submitted DATE DEFAULT (DATE('now'))
    )''')
    conn.commit()
    conn.close()

init_db()

# Utility: get DB connection
def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # Basic server-side validation
    name = request.form.get('name', '').strip()
    room = request.form.get('room', '').strip()
    meal = request.form.get('meal', '').strip()
    rating = request.form.get('rating', '').strip()
    comment = request.form.get('comment', '').strip()

    if not name:
        flash('Name is required.', 'danger')
        return redirect(url_for('index'))
    if not meal:
        flash('Meal type is required.', 'danger')
        return redirect(url_for('index'))
    if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
        flash('Rating must be an integer between 1 and 5.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (student_name, room_number, meal_type, rating, comment, date_submitted) VALUES (?, ?, ?, ?, ?, ?)",
        (name, room, meal, int(rating), comment, date.today())
    )
    conn.commit()
    conn.close()

    flash('Thank you — your feedback has been submitted.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT meal_type, ROUND(AVG(rating),2) as avg_rating, COUNT(*) as count FROM feedback GROUP BY meal_type")
    data = cursor.fetchall()

    # If there are meal types missing (e.g., no Breakfast entries), ensure labels exist for charts
    conn.close()
    return render_template('dashboard.html', data=data)

@app.route('/summary')
def summary():
    conn = get_db_conn()
    cursor = conn.cursor()

    # Meal-wise average rating
    cursor.execute("SELECT meal_type, AVG(rating) as avg FROM feedback GROUP BY meal_type")
    meal_data = cursor.fetchall()
    meal_labels = [row['meal_type'] for row in meal_data]
    meal_avg_ratings = [round(row['avg'],2) for row in meal_data]

    # Feedback distribution: Good (4-5), Average (3), Poor (1-2)
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating >= 4")
    good = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 3")
    average = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating <= 2")
    poor = cursor.fetchone()[0]

    feedback_distribution = [good, average, poor]

    # For weekly trend (optional): last 7 days average
    cursor.execute('''
        SELECT date_submitted as day, ROUND(AVG(rating),2) as avg
        FROM feedback
        WHERE date_submitted >= DATE('now','-6 days')
        GROUP BY date_submitted
        ORDER BY date_submitted
    ''')
    trend_rows = cursor.fetchall()
    trend_labels = [row['day'] for row in trend_rows]
    trend_avgs = [round(row['avg'],2) for row in trend_rows]

    conn.close()

    return render_template('summary.html',
                           meal_labels=meal_labels,
                           meal_avg_ratings=meal_avg_ratings,
                           feedback_distribution=feedback_distribution,
                           trend_labels=trend_labels,
                           trend_avgs=trend_avgs)

if __name__ == '__main__':
    app.run(debug=True)