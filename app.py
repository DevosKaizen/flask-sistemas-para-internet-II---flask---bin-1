from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from models import db, User, Class, ClassStudent
import os
from flask_migrate import Migrate

# Cria uma instância do Flask
app = Flask(__name__)

# Configurações do aplicativo Flask
app.config['SECRET_KEY'] = 'your_secret_key'  # Chave secreta para sessões
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # URI do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa o rastreamento de modificações do SQLAlchemy

# Inicializa o Bootstrap com o aplicativo Flask
Bootstrap(app)

# Inicializa o SQLAlchemy com o aplicativo Flask
db.init_app(app)

# Inicializa o Flask-Migrate com o aplicativo Flask e o banco de dados
migrate = Migrate(app, db)

# Cria todas as tabelas do banco de dados se ainda não existirem
with app.app_context():
    db.create_all()

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtém os dados do formulário de login
        username = request.form['username']
        password = request.form['password']
        # Verifica se o usuário existe no banco de dados
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Armazena o ID e o papel do usuário na sessão
            session['user_id'] = user.id
            session['user_role'] = user.role
            # Redireciona para o dashboard se o usuário for professor, ou para as classes se for aluno
            if user.role == 'professor':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('classes'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Rota para registro de novos usuários
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtém os dados do formulário de registro
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        # Cria um novo usuário e adiciona ao banco de dados
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota para o dashboard do professor
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session and session['user_role'] == 'professor':
        # Obtém todos os alunos e professores do banco de dados
        students = User.query.filter_by(role='aluno').all()
        professors = User.query.filter_by(role='professor').all()
        return render_template('dashboard.html', students=students, professors=professors)
    return redirect(url_for('login'))

# Rota para criação de novas classes
@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if 'user_id' in session and session['user_role'] == 'professor':
        if request.method == 'POST':
            # Obtém os dados do formulário de criação de classe
            class_name = request.form['class_name']
            student_ids = request.form.getlist('students')
            # Cria uma nova classe e adiciona ao banco de dados
            new_class = Class(name=class_name)
            db.session.add(new_class)
            db.session.commit()
            # Adiciona os alunos à nova classe
            for student_id in student_ids:
                student = User.query.get(student_id)
                class_student = ClassStudent(class_id=new_class.id, student_id=student.id)
                db.session.add(class_student)
            db.session.commit()
            return redirect(url_for('dashboard'))
        # Obtém todos os alunos do banco de dados
        students = User.query.filter_by(role='aluno').all()
        return render_template('create_class.html', students=students)
    return redirect(url_for('login'))

# Rota para visualização das classes pelos alunos
@app.route('/classes')
def classes():
    if 'user_id' in session and session['user_role'] == 'aluno':
        # Obtém todas as classes do banco de dados
        classes = Class.query.all()
        return render_template('classes.html', classes=classes)
    return redirect(url_for('login'))

# Rota para exclusão de alunos
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        # Obtém o aluno a ser excluído
        student = User.query.get(student_id)
        if student and student.role == 'aluno':
            # Remove todas as associações na tabela class_student
            ClassStudent.query.filter_by(student_id=student_id).delete()
            # Exclui o aluno do banco de dados
            db.session.delete(student)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota para exclusão de professores
@app.route('/delete_professor/<int:professor_id>', methods=['POST'])
def delete_professor(professor_id):
    if 'user_id' in session and session['user_role'] == 'professor':
        # Obtém o professor a ser excluído
        professor = User.query.get(professor_id)
        if professor and professor.role == 'professor':
            # Remove todas as associações na tabela class_student
            ClassStudent.query.filter_by(student_id=professor_id).delete()
            # Exclui o professor do banco de dados
            db.session.delete(professor)
            db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota para limpar o banco de dados
@app.route('/clear_db', methods=['POST'])
def clear_db():
    if 'user_id' in session and session['user_role'] == 'professor':
        # Remove todas as tabelas do banco de dados
        db.drop_all()
        # Cria todas as tabelas novamente
        db.create_all()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Executa o aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True)