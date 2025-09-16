from flask import Flask, render_template, request, redirect, session
import mysql.connector, hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection function
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="3005",
        database="task_db"
    )

# Home → Redirect to dashboard if logged in
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (session['user_id'],))
    tasks = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('dashboard.html', tasks=tasks)

# Login page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template('login.html')

# Register page
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        db = get_db()
        cur = db.cursor(dictionary=True)

        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            db.close()
            return render_template("register.html", error="Email already registered")

        # Insert new user
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password))
        db.commit()
        cur.close()
        db.close()

        return redirect("/login")
    
    return render_template("register.html")

# Add Task Page
@app.route('/add_task_page')
def add_task_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("add_task.html")

# Add Task action
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']
    description = request.form['description']
    priority = request.form.get('priority')
    deadline = request.form.get('deadline')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (title, description, priority, deadline, user_id) VALUES (%s,%s,%s,%s,%s)",
                   (title, description, priority, deadline, session['user_id']))
    db.commit()
    cursor.close()
    db.close()

    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
