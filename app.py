from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from models import db, User, Class, ClassStudent
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_role'] = user.role
            if user.role == 'professor':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('classes'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and session['user_role'] == 'professor':
        students = User.query.filter_by(role='aluno').all()
        professors = User.query.filter_by(role='professor').all()
        return render_template('dashboard.html', students=students, professors=professors)
    return redirect(url_for('login'))

@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if 'user_id' in session and session['user_role'] == 'professor':
        if request.method == 'POST':
            class_name = request.form['class_name']
            student_ids = request.form.getlist('students')
            new_class = Class(name=class_name)
            db.session.add(new_class)
            db.session.commit()
            for student_id in student_ids:
                student = User.query.get(student_id)
                class_student = ClassStudent(class_id=new_class.id, student_id=student.id)
                db.session.add(class_student)
            db.session.commit()
            return redirect(url_for('dashboard'))
        students = User.query.filter_by(role='aluno').all()
        return render_template('create_class.html', students=students)
    return redirect(url_for('login'))

@app.route('/classes')
def classes():
    if 'user_id' in session and session['user_role'] == 'aluno':
        classes = Class.query.all()
        return render_template('classes.html', classes=classes)
    return redirect(url_for('login'))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        student = User.query.get(student_id)
        if student and student.role == 'aluno':
            db.session.delete(student)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/delete_professor/<int:professor_id>', methods=['POST'])
def delete_professor(professor_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        professor = User.query.get(professor_id)
        if professor and professor.role == 'professor':
            db.session.delete(professor)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)