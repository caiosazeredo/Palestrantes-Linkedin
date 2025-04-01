from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models.usuario import Usuario
from app.forms.auth import LoginForm, RegistroForm, AlterarSenhaForm, CadastroForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        # Verificar se o usuário existe e a senha está correta
        if usuario is None or not usuario.check_senha(form.senha.data):
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        # Realizar o login do usuário
        login_user(usuario, remember=form.lembrar_me.data)
        
        # Redirecionar para a próxima página se existir
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash('Login realizado com sucesso!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    """Rota para realizar logout"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro para novos usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = CadastroForm()
    if form.validate_on_submit():
        # Criar novo usuário
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            is_admin=False  # Usuários cadastrados nunca são admin por padrão
        )
        usuario.set_senha(form.senha.data)
        
        # Salvar no banco
        db.session.add(usuario)
        db.session.commit()
        
        # Login automático
        login_user(usuario)
        
        flash('Cadastro realizado com sucesso! Bem-vindo(a) ao sistema.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/cadastro.html', form=form)

@bp.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    """
    Página de registro de novos usuários
    Apenas usuários admin podem registrar novos usuários
    """
    # Verificar se o usuário atual é admin
    if not current_user.is_admin:
        flash('Permissão negada. Apenas administradores podem registrar novos usuários.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        # Criar novo usuário
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        usuario.set_senha(form.senha.data)
        
        # Salvar no banco
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Usuário {usuario.nome} registrado com sucesso!', 'success')
        return redirect(url_for('auth.listar_usuarios'))
    
    return render_template('auth/registro.html', form=form)

@bp.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Página para o usuário alterar sua própria senha"""
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        # Verificar se a senha atual está correta
        if not current_user.check_senha(form.senha_atual.data):
            flash('Senha atual incorreta', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        # Alterar a senha
        current_user.set_senha(form.nova_senha.data)
        db.session.commit()
        
        flash('Sua senha foi alterada com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/alterar_senha.html', form=form)

@bp.route('/usuarios')
@login_required
def listar_usuarios():
    """Página para listar todos os usuários (apenas admin)"""
    # Verificar se o usuário atual é admin
    if not current_user.is_admin:
        flash('Permissão negada. Apenas administradores podem ver a lista de usuários.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('auth/usuarios.html', usuarios=usuarios)

@bp.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    """Rota para excluir um usuário"""
    # Verificar se o usuário atual é admin
    if not current_user.is_admin:
        flash('Permissão negada. Apenas administradores podem excluir usuários.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Não permitir que um usuário exclua a si mesmo
    if current_user.id == id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('auth.listar_usuarios'))
    
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuário {usuario.nome} excluído com sucesso!', 'success')
    return redirect(url_for('auth.listar_usuarios'))