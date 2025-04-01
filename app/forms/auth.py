from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.usuario import Usuario

class LoginForm(FlaskForm):
    """Formulário de login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class CadastroForm(FlaskForm):
    """Formulário para cadastro de usuários (público)"""
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    senha = PasswordField('Senha', validators=[
        DataRequired(), 
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(), 
        EqualTo('senha', message='As senhas não conferem')
    ])
    submit = SubmitField('Cadastrar')
    
    def validate_email(self, email):
        """Validar se o email já está em uso"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is not None:
            raise ValidationError('Este email já está sendo usado. Por favor, use outro.')

class RegistroForm(FlaskForm):
    """Formulário para registro de novos usuários (admin)"""
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    senha = PasswordField('Senha', validators=[
        DataRequired(), 
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        DataRequired(), 
        EqualTo('senha', message='As senhas não conferem')
    ])
    is_admin = BooleanField('É administrador')
    submit = SubmitField('Registrar')
    
    def validate_email(self, email):
        """Validar se o email já está em uso"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is not None:
            raise ValidationError('Este email já está sendo usado. Por favor, use outro.')

class AlterarSenhaForm(FlaskForm):
    """Formulário para alteração de senha"""
    senha_atual = PasswordField('Senha atual', validators=[DataRequired()])
    nova_senha = PasswordField('Nova senha', validators=[
        DataRequired(), 
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_nova_senha = PasswordField('Confirmar nova senha', validators=[
        DataRequired(), 
        EqualTo('nova_senha', message='As senhas não conferem')
    ])
    submit = SubmitField('Alterar senha')