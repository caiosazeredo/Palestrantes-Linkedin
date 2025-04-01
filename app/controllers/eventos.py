from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from datetime import datetime

from app import db
from app.models.evento import Evento, AvaliacaoPalestrante
from app.models.palestrante import Palestrante
from app.forms.evento import EventoForm, AvaliacaoForm

bp = Blueprint('eventos', __name__)

@bp.route('/')
@login_required
def index():
    """Listar todos os eventos cadastrados"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Eventos por página
    
    # Filtros
    nome = request.args.get('nome', '')
    periodo = request.args.get('periodo', 'todos')  # 'passados', 'proximos', 'todos'
    
    query = Evento.query
    
    # Aplicar filtros se fornecidos
    if nome:
        query = query.filter(Evento.nome.ilike(f'%{nome}%'))
    
    # Filtrar por período
    hoje = datetime.utcnow()
    if periodo == 'passados':
        query = query.filter(Evento.data_fim < hoje)
    elif periodo == 'proximos':
        query = query.filter(Evento.data_inicio >= hoje)
    
    # Ordenar e paginar
    eventos = query.order_by(Evento.data_inicio.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'eventos/index.html', 
        eventos=eventos,
        nome_filtro=nome,
        periodo_filtro=periodo
    )

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo evento"""
    form = EventoForm()
    
    # Preencher as opções de palestrantes
    todos_palestrantes = Palestrante.query.order_by(Palestrante.nome).all()
    form.palestrantes.choices = [(p.id, p.nome) for p in todos_palestrantes]
    
    if form.validate_on_submit():
        # Criar novo evento
        evento = Evento(
            nome=form.nome.data,
            descricao=form.descricao.data,
            data_inicio=form.data_inicio.data,
            data_fim=form.data_fim.data,
            local=form.local.data
        )
        
        # Adicionar palestrantes
        for palestrante_id in form.palestrantes.data:
            palestrante = Palestrante.query.get(palestrante_id)
            if palestrante:
                evento.palestrantes.append(palestrante)
                
                # Marcar palestrante como já tendo participado
                palestrante.ja_participou = True
        
        # Salvar no banco
        db.session.add(evento)
        db.session.commit()
        
        flash(f'Evento "{evento.nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('eventos.detalhes', id=evento.id))
    
    return render_template('eventos/form.html', form=form, title="Novo Evento")

@bp.route('/<int:id>')
@login_required
def detalhes(id):
    """Visualizar detalhes de um evento"""
    evento = Evento.query.get_or_404(id)
    form_avaliacao = AvaliacaoForm()
    
    # Verificar se o evento já aconteceu (para permitir avaliações)
    hoje = datetime.utcnow()
    evento_passado = evento.data_fim < hoje
    
    # Obter avaliações já registradas
    avaliacoes = AvaliacaoPalestrante.query.filter_by(evento_id=evento.id).all()
    
    return render_template(
        'eventos/detalhes.html', 
        evento=evento, 
        evento_passado=evento_passado,
        form_avaliacao=form_avaliacao,
        avaliacoes=avaliacoes
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar evento existente"""
    evento = Evento.query.get_or_404(id)
    form = EventoForm(obj=evento)
    
    # Preencher as opções de palestrantes
    todos_palestrantes = Palestrante.query.order_by(Palestrante.nome).all()
    form.palestrantes.choices = [(p.id, p.nome) for p in todos_palestrantes]
    
    # Pré-selecionar palestrantes do evento
    if request.method == 'GET':
        form.palestrantes.data = [p.id for p in evento.palestrantes]
    
    if form.validate_on_submit():
        # Atualizar dados do evento
        evento.nome = form.nome.data
        evento.descricao = form.descricao.data
        evento.data_inicio = form.data_inicio.data
        evento.data_fim = form.data_fim.data
        evento.local = form.local.data
        
        # Atualizar palestrantes (limpar e adicionar novamente)
        palestrantes_antigos = list(evento.palestrantes)
        evento.palestrantes = []
        
        for palestrante_id in form.palestrantes.data:
            palestrante = Palestrante.query.get(palestrante_id)
            if palestrante:
                evento.palestrantes.append(palestrante)
                
                # Marcar palestrante como já tendo participado
                palestrante.ja_participou = True
        
        # Verificar palestrantes removidos e atualizar flag ja_participou se necessário
        for p in palestrantes_antigos:
            if p not in evento.palestrantes:
                # Verificar se ainda participa de algum outro evento
                outros_eventos = Evento.query.filter(
                    Evento.palestrantes.contains(p),
                    Evento.id != evento.id
                ).count()
                
                if outros_eventos == 0:
                    p.ja_participou = False
        
        # Salvar no banco
        db.session.commit()
        
        flash(f'Evento "{evento.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('eventos.detalhes', id=evento.id))
    
    return render_template('eventos/form.html', form=form, title="Editar Evento", evento=evento)

@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir um evento"""
    evento = Evento.query.get_or_404(id)
    nome = evento.nome  # Guardar o nome para exibir na mensagem
    
    # Lista de palestrantes antes de excluir
    palestrantes = list(evento.palestrantes)
    
    # Excluir avaliações do evento
    AvaliacaoPalestrante.query.filter_by(evento_id=evento.id).delete()
    
    # Excluir do banco
    db.session.delete(evento)
    db.session.commit()
    
    # Verificar palestrantes e atualizar flag ja_participou se necessário
    for p in palestrantes:
        outros_eventos = Evento.query.filter(
            Evento.palestrantes.contains(p)
        ).count()
        
        if outros_eventos == 0:
            p.ja_participou = False
            db.session.add(p)
    
    db.session.commit()
    
    flash(f'Evento "{nome}" excluído com sucesso!', 'success')
    return redirect(url_for('eventos.index'))

@bp.route('/<int:evento_id>/avaliar/<int:palestrante_id>', methods=['POST'])
@login_required
def avaliar_palestrante(evento_id, palestrante_id):
    """Registrar avaliação de um palestrante em um evento"""
    evento = Evento.query.get_or_404(evento_id)
    palestrante = Palestrante.query.get_or_404(palestrante_id)
    
    # Verificar se o palestrante realmente participou do evento
    if palestrante not in evento.palestrantes:
        flash('Este palestrante não está associado a este evento.', 'danger')
        return redirect(url_for('eventos.detalhes', id=evento_id))
    
    # Verificar se o evento já aconteceu
    hoje = datetime.utcnow()
    if evento.data_fim >= hoje:
        flash('Só é possível avaliar palestrantes após o término do evento.', 'danger')
        return redirect(url_for('eventos.detalhes', id=evento_id))
    
    form = AvaliacaoForm()
    
    if form.validate_on_submit():
        # Verificar se já existe avaliação
        avaliacao_existente = AvaliacaoPalestrante.query.filter_by(
            evento_id=evento_id,
            palestrante_id=palestrante_id
        ).first()
        
        if avaliacao_existente:
            # Atualizar avaliação existente
            avaliacao_existente.nota = form.nota.data
            avaliacao_existente.comentario = form.comentario.data
            flash('Avaliação atualizada com sucesso!', 'success')
        else:
            # Criar nova avaliação
            avaliacao = AvaliacaoPalestrante(
                evento_id=evento_id,
                palestrante_id=palestrante_id,
                nota=form.nota.data,
                comentario=form.comentario.data
            )
            db.session.add(avaliacao)
            flash('Avaliação registrada com sucesso!', 'success')
        
        # Atualizar nota média do palestrante
        todas_avaliacoes = AvaliacaoPalestrante.query.filter_by(
            palestrante_id=palestrante_id
        ).all()
        
        total_notas = sum(a.nota for a in todas_avaliacoes)
        media = total_notas / len(todas_avaliacoes) if todas_avaliacoes else 0
        
        palestrante.avaliacao_media = round(media, 1)
        
        # Salvar no banco
        db.session.commit()
    
    return redirect(url_for('eventos.detalhes', id=evento_id))