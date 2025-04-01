from app import db
from datetime import datetime

# Tabela de associação entre palestrantes e eventos
palestrante_eventos = db.Table(
    'palestrante_eventos',
    db.Column('palestrante_id', db.Integer, db.ForeignKey('palestrante.id'), primary_key=True),
    db.Column('evento_id', db.Integer, db.ForeignKey('evento.id'), primary_key=True)
)

class Evento(db.Model):
    """Modelo para eventos do Senac Cápsula"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(100))
    
    # Avaliações do evento
    avaliacao_media = db.Column(db.Float, default=0.0)
    numero_avaliacoes = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    palestrantes = db.relationship(
        'Palestrante',
        secondary=palestrante_eventos,
        backref=db.backref('eventos', lazy='dynamic')
    )
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evento {self.nome}>'

class AvaliacaoPalestrante(db.Model):
    """Modelo para avaliações de palestrantes em eventos"""
    id = db.Column(db.Integer, primary_key=True)
    palestrante_id = db.Column(db.Integer, db.ForeignKey('palestrante.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.Text)
    
    # Definindo uma chave única composta para garantir que um palestrante 
    # seja avaliado apenas uma vez por evento
    __table_args__ = (
        db.UniqueConstraint('palestrante_id', 'evento_id', name='uq_avaliacao_palestrante_evento'),
    )
    
    # Relacionamentos
    palestrante = db.relationship('Palestrante', backref=db.backref('avaliacoes', lazy='dynamic'))
    evento = db.relationship('Evento', backref=db.backref('avaliacoes_palestrantes', lazy='dynamic'))
    
    # Timestamp
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AvaliacaoPalestrante {self.palestrante_id} - {self.evento_id}>'