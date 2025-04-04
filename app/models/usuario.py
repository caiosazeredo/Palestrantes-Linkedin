from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_senha(self, senha):
        """Define a senha criptografada para o usuário"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

@login.user_loader
def load_user(id):
    """Função necessária para o Flask-Login carregar o usuário da sessão"""
    return Usuario.query.get(int(id))
