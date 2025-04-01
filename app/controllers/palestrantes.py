from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models.palestrante import Palestrante, PalavraChave
from app.forms.palestrante import PalestranteForm, BuscarPalestranteForm, PalavraChaveForm
from app.services.linkedin_crawler import LinkedInCrawler

bp = Blueprint('palestrantes', __name__)

@bp.route('/')
@login_required
def index():
    """Listar todos os palestrantes cadastrados"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Palestrantes por página
    
    # Filtros
    nome = request.args.get('nome', '')
    especialidade = request.args.get('especialidade', '')
    
    query = Palestrante.query
    
    # Aplicar filtros se fornecidos
    if nome:
        query = query.filter(Palestrante.nome.ilike(f'%{nome}%'))
    
    if especialidade:
        palavra = PalavraChave.query.filter(PalavraChave.palavra.ilike(f'%{especialidade}%')).first()
        if palavra:
            query = query.filter(Palestrante.palavras_chave.contains(palavra))
    
    # Ordenar e paginar
    palestrantes = query.order_by(Palestrante.nome).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'palestrantes/index.html', 
        palestrantes=palestrantes,
        nome_filtro=nome,
        especialidade_filtro=especialidade
    )

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo palestrante"""
    form = PalestranteForm()
    
    # Preencher as opções de palavras-chave
    todas_palavras = PalavraChave.query.order_by(PalavraChave.palavra).all()
    form.palavras_chave.choices = [(p.id, p.palavra) for p in todas_palavras]
    
    if form.validate_on_submit():
        # Criar novo palestrante
        palestrante = Palestrante(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            bio=form.bio.data,
            linkedin_url=form.linkedin_url.data
        )
        
        # Processar upload da foto, se fornecida
        if form.foto.data:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{form.foto.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.foto.data.save(filepath)
            palestrante.foto_url = f"/static/uploads/{filename}"
        
        # Adicionar palavras-chave
        for palavra_id in form.palavras_chave.data:
            palavra = PalavraChave.query.get(palavra_id)
            if palavra:
                palestrante.palavras_chave.append(palavra)
        
        # Salvar no banco
        db.session.add(palestrante)
        db.session.commit()
        
        flash(f'Palestrante {palestrante.nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('palestrantes.detalhes', id=palestrante.id))
    
    return render_template('palestrantes/form.html', form=form, title="Novo Palestrante")

@bp.route('/<int:id>')
@login_required
def detalhes(id):
    """Visualizar detalhes de um palestrante"""
    palestrante = Palestrante.query.get_or_404(id)
    return render_template('palestrantes/detalhes.html', palestrante=palestrante)

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar palestrante existente"""
    palestrante = Palestrante.query.get_or_404(id)
    form = PalestranteForm(obj=palestrante)
    
    # Preencher as opções de palavras-chave
    todas_palavras = PalavraChave.query.order_by(PalavraChave.palavra).all()
    form.palavras_chave.choices = [(p.id, p.palavra) for p in todas_palavras]
    
    # Pré-selecionar palavras-chave do palestrante
    if request.method == 'GET':
        form.palavras_chave.data = [p.id for p in palestrante.palavras_chave]
    
    if form.validate_on_submit():
        # Atualizar dados do palestrante
        palestrante.nome = form.nome.data
        palestrante.email = form.email.data
        palestrante.telefone = form.telefone.data
        palestrante.bio = form.bio.data
        palestrante.linkedin_url = form.linkedin_url.data
        
        # Processar upload da foto, se fornecida
        if form.foto.data:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{form.foto.data.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.foto.data.save(filepath)
            palestrante.foto_url = f"/static/uploads/{filename}"
        
        # Atualizar palavras-chave (limpar e adicionar novamente)
        palestrante.palavras_chave = []
        for palavra_id in form.palavras_chave.data:
            palavra = PalavraChave.query.get(palavra_id)
            if palavra:
                palestrante.palavras_chave.append(palavra)
        
        # Salvar no banco
        db.session.commit()
        
        flash(f'Palestrante {palestrante.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('palestrantes.detalhes', id=palestrante.id))
    
    return render_template('palestrantes/form.html', form=form, title="Editar Palestrante", palestrante=palestrante)

@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir um palestrante"""
    palestrante = Palestrante.query.get_or_404(id)
    nome = palestrante.nome  # Guardar o nome para exibir na mensagem
    
    # Excluir do banco
    db.session.delete(palestrante)
    db.session.commit()
    
    flash(f'Palestrante {nome} excluído com sucesso!', 'success')
    return redirect(url_for('palestrantes.index'))

@bp.route('/buscar-linkedin', methods=['GET', 'POST'])
@login_required
def buscar_linkedin():
    """Buscar palestrantes no LinkedIn"""
    form = BuscarPalestranteForm()
    resultados = []
    
    if form.validate_on_submit():
        try:
            # Inicializar o crawler
            crawler = LinkedInCrawler()
            
            # Realizar a busca
            palavras_chave = form.palavras_chave.data.split(',')
            palavras_chave = [p.strip() for p in palavras_chave if p.strip()]
            
            resultados = crawler.buscar_profissionais(
                palavras_chave=palavras_chave,
                min_seguidores=form.min_seguidores.data or 0,
                localizacao=form.localizacao.data or None,
                max_resultados=form.max_resultados.data or 10
            )
            
            if not resultados:
                flash('Nenhum resultado encontrado para os critérios informados.', 'info')
            
        except Exception as e:
            flash(f'Erro ao realizar busca no LinkedIn: {str(e)}', 'danger')
    
    return render_template('palestrantes/buscar_linkedin.html', form=form, resultados=resultados)

@bp.route('/importar-linkedin', methods=['POST'])
@login_required
def importar_linkedin():
    """Importar um perfil do LinkedIn para o banco de dados"""
    # Verificar se os dados necessários foram enviados
    if not all(k in request.form for k in ('nome', 'cargo_atual', 'perfil_url')):
        flash('Dados insuficientes para importar o perfil.', 'danger')
        return redirect(url_for('palestrantes.buscar_linkedin'))
    
    # Verificar se já existe palestrante com esta URL
    perfil_url = request.form.get('perfil_url')
    existente = Palestrante.query.filter_by(linkedin_url=perfil_url).first()
    
    if existente:
        flash(f'Palestrante {existente.nome} já existe no sistema com este perfil do LinkedIn.', 'warning')
        return redirect(url_for('palestrantes.detalhes', id=existente.id))
    
    # Criar novo palestrante com os dados do LinkedIn
    palestrante = Palestrante(
        nome=request.form.get('nome'),
        linkedin_url=perfil_url,
        linkedin_cargo_atual=request.form.get('cargo_atual'),
        linkedin_empresa_atual=request.form.get('empresa_atual'),
        bio=request.form.get('bio', ''),
        foto_url=request.form.get('foto_url', ''),
        linkedin_seguidores=request.form.get('seguidores', 0),
        linkedin_ultima_atualizacao=datetime.utcnow()
    )
    
    # Adicionar habilidades como palavras-chave
    if 'habilidades' in request.form and request.form.get('habilidades'):
        habilidades = request.form.get('habilidades').split(',')
        for hab in habilidades:
            hab = hab.strip()
            if hab:
                # Verificar se a palavra-chave já existe ou criar nova
                palavra = PalavraChave.query.filter_by(palavra=hab).first()
                if not palavra:
                    palavra = PalavraChave(palavra=hab)
                    db.session.add(palavra)
                
                # Adicionar ao palestrante
                palestrante.palavras_chave.append(palavra)
    
    # Salvar no banco
    db.session.add(palestrante)
    db.session.commit()
    
    flash(f'Palestrante {palestrante.nome} importado com sucesso do LinkedIn!', 'success')
    return redirect(url_for('palestrantes.detalhes', id=palestrante.id))

@bp.route('/atualizar-linkedin/<int:id>', methods=['POST'])
@login_required
def atualizar_linkedin(id):
    """Atualizar dados de um palestrante a partir do LinkedIn"""
    palestrante = Palestrante.query.get_or_404(id)
    
    # Verificar se o palestrante tem URL do LinkedIn
    if not palestrante.linkedin_url:
        flash('Este palestrante não possui URL do LinkedIn cadastrada.', 'danger')
        return redirect(url_for('palestrantes.detalhes', id=palestrante.id))
    
    try:
        # Inicializar o crawler
        crawler = LinkedInCrawler()
        
        # Obter informações atualizadas
        info = crawler.obter_info_perfil(palestrante.linkedin_url)
        
        # Atualizar dados do palestrante
        if info.get('nome'):
            palestrante.nome = info['nome']
        if info.get('cargo_atual'):
            palestrante.linkedin_cargo_atual = info['cargo_atual']
        if info.get('empresa_atual'):
            palestrante.linkedin_empresa_atual = info['empresa_atual']
        if info.get('bio'):
            palestrante.bio = info['bio']
        if info.get('foto_url'):
            palestrante.foto_url = info['foto_url']
        if info.get('seguidores'):
            palestrante.linkedin_seguidores = info['seguidores']
        
        # Atualizar habilidades como palavras-chave
        if info.get('habilidades'):
            for hab in info['habilidades']:
                hab = hab.strip()
                if hab:
                    # Verificar se a palavra-chave já existe ou criar nova
                    palavra = PalavraChave.query.filter_by(palavra=hab).first()
                    if not palavra:
                        palavra = PalavraChave(palavra=hab)
                        db.session.add(palavra)
                    
                    # Adicionar ao palestrante se ainda não tiver
                    if palavra not in palestrante.palavras_chave:
                        palestrante.palavras_chave.append(palavra)
        
        # Atualizar timestamp
        palestrante.linkedin_ultima_atualizacao = datetime.utcnow()
        
        # Salvar no banco
        db.session.commit()
        
        flash(f'Dados do palestrante {palestrante.nome} atualizados com sucesso do LinkedIn!', 'success')
    
    except Exception as e:
        flash(f'Erro ao atualizar dados do LinkedIn: {str(e)}', 'danger')
    
    return redirect(url_for('palestrantes.detalhes', id=palestrante.id))

@bp.route('/palavras-chave')
@login_required
def palavras_chave():
    """Gerenciar palavras-chave/especialidades"""
    form = PalavraChaveForm()
    palavras = PalavraChave.query.order_by(PalavraChave.palavra).all()
    
    return render_template('palestrantes/palavras_chave.html', form=form, palavras=palavras)

@bp.route('/palavras-chave/nova', methods=['POST'])
@login_required
def nova_palavra_chave():
    """Adicionar nova palavra-chave"""
    form = PalavraChaveForm()
    
    if form.validate_on_submit():
        # Verificar se já existe
        existente = PalavraChave.query.filter_by(palavra=form.palavra.data).first()
        
        if existente:
            flash(f'A palavra-chave "{form.palavra.data}" já existe.', 'warning')
        else:
            # Criar nova palavra-chave
            palavra = PalavraChave(palavra=form.palavra.data)
            db.session.add(palavra)
            db.session.commit()
            
            flash(f'Palavra-chave "{palavra.palavra}" adicionada com sucesso!', 'success')
    
    return redirect(url_for('palestrantes.palavras_chave'))

@bp.route('/palavras-chave/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_palavra_chave(id):
    """Excluir uma palavra-chave"""
    palavra = PalavraChave.query.get_or_404(id)
    
    # Verificar se possui palestrantes associados
    if palavra.palestrantes.count() > 0:
        flash(f'Não é possível excluir a palavra-chave "{palavra.palavra}" pois está sendo usada por palestrantes.', 'danger')
    else:
        db.session.delete(palavra)
        db.session.commit()
        
        flash(f'Palavra-chave "{palavra.palavra}" excluída com sucesso!', 'success')
    
    return redirect(url_for('palestrantes.palavras_chave'))