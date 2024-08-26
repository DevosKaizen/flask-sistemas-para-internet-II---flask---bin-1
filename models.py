from flask_sqlalchemy import SQLAlchemy

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy()

# Modelo para a tabela User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10), nullable=False)

# Modelo para a tabela Class
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    # Relacionamento muitos-para-muitos com a tabela User
    students = db.relationship('User', secondary='class_student', backref='classes')

# Modelo para a tabela de associação entre Class e User
class ClassStudent(db.Model):
    __tablename__ = 'class_student'
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)