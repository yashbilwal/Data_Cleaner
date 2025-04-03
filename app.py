import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from config import Config

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize MySQL
mysql = MySQL(app)

# Database initialization
def init_db():
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS uploads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    cleaned_filename VARCHAR(255) NOT NULL,
                    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            mysql.connection.commit()
            cur.close()
        print("Database initialized")
    except Exception as e:
        print(f"Database error: {e}")

init_db()

# Import data cleaner
from utils.data_cleaner import clean_sales_data

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def home():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user and check_password_hash(user[1], password):
                session['email'] = email
                session['user_id'] = user[0]
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            
            flash('Invalid email or password', 'danger')
        except Exception as e:
            flash('Database error', 'danger')
            print(f"Login error: {e}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, hashed_password)
            )
            mysql.connection.commit()
            cur.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, original_filename, cleaned_filename, uploaded_at 
            FROM uploads 
            WHERE user_id = %s 
            ORDER BY uploaded_at DESC
        """, (session['user_id'],))
        columns = [column[0] for column in cur.description]
        uploads = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
    except Exception as e:
        flash('Error loading files', 'danger')
        print(f"Dashboard error: {e}")
        uploads = []
    
    return render_template('dashboard.html', uploads=uploads)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                output_filename = f"cleaned_{filename}"
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                clean_sales_data(filepath, output_path)
                
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO uploads (user_id, original_filename, cleaned_filename) VALUES (%s, %s, %s)",
                    (session['user_id'], filename, output_filename)
                )
                mysql.connection.commit()
                cur.close()
                
                flash('File processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash('Error processing file', 'danger')
                print(f"Upload error: {e}")
                return redirect(request.url)
        else:
            flash('Only CSV files allowed', 'danger')
    
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT 1 FROM uploads WHERE user_id = %s AND cleaned_filename = %s",
            (session['user_id'], filename)
        )
        if not cur.fetchone():
            flash('File not found', 'danger')
            return redirect(url_for('dashboard'))
        cur.close()
    except Exception as e:
        flash('Error verifying file', 'danger')
        print(f"Download verification error: {e}")
        return redirect(url_for('dashboard'))
    
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)