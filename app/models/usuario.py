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
ECHO est† desativado.
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
ECHO est† desativado.
    def set_senha(self, senha):
        """Define a senha criptografada para o usu√°rio"""
        self.senha_hash = generate_password_hash(senha)
ECHO est† desativado.
    def check_senha(self, senha):
        """Verifica se a senha est√° correta"""
        return check_password_hash(self.senha_hash, senha)
ECHO est† desativado.
    def __repr__(self):

@login.user_loader
def load_user(id):
    """Fun√ß√£o necess√°ria para o Flask-Login carregar o usu√°rio da sess√£o"""
    return Usuario.query.get(int(id))
