from app import db
from datetime import datetime

# Tabela de associação entre palestrantes e palavras-chave
palestrante_palavras_chave = db.Table(
    'palestrante_palavras_chave',
    db.Column('palestrante_id', db.Integer, db.ForeignKey('palestrante.id'), primary_key=True),
    db.Column('palavra_chave_id', db.Integer, db.ForeignKey('palavra_chave.id'), primary_key=True)
)

class PalavraChave(db.Model):
    """Modelo para palavras-chave/especialidades dos palestrantes"""
    id = db.Column(db.Integer, primary_key=True)
    palavra = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<PalavraChave {self.palavra}>'

class Palestrante(db.Model):
    """Modelo para palestrantes"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    
    # Dados do LinkedIn
    linkedin_url = db.Column(db.String(255))
    linkedin_seguidores = db.Column(db.Integer)
    linkedin_cargo_atual = db.Column(db.String(100))
    linkedin_empresa_atual = db.Column(db.String(100))
    linkedin_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Informações adicionais
    ja_participou = db.Column(db.Boolean, default=False)
    avaliacao_media = db.Column(db.Float, default=0.0)
    
    # Relacionamentos
    palavras_chave = db.relationship(
        'PalavraChave', 
        secondary=palestrante_palavras_chave,
        backref=db.backref('palestrantes', lazy='dynamic')
    )
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Palestrante {self.nome}>'