from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.palestrante import Palestrante
from app.models.evento import Evento

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Página inicial"""
    # Redirecionamento para o dashboard se já estiver logado
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal com visão geral"""
    # Obter estatísticas para o dashboard
    total_palestrantes = Palestrante.query.count()
    total_eventos = Evento.query.count()
    
    # Palestrantes recentes
    palestrantes_recentes = Palestrante.query.order_by(
        Palestrante.data_criacao.desc()
    ).limit(5).all()
    
    # Eventos próximos
    from datetime import datetime
    eventos_proximos = Evento.query.filter(
        Evento.data_inicio >= datetime.utcnow()
    ).order_by(Evento.data_inicio).limit(5).all()
    
    # Palestrantes top avaliados
    palestrantes_top = Palestrante.query.filter(
        Palestrante.avaliacao_media > 0
    ).order_by(Palestrante.avaliacao_media.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        total_palestrantes=total_palestrantes,
        total_eventos=total_eventos,
        palestrantes_recentes=palestrantes_recentes,
        eventos_proximos=eventos_proximos,
        palestrantes_top=palestrantes_top
    )

@bp.route('/sobre')
def sobre():
    """Página sobre o sistema"""
    return render_template('sobre.html')