from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectMultipleField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, NumberRange

class PalestranteForm(FlaskForm):
    """Formulário para cadastro e edição de palestrantes"""
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    bio = TextAreaField('Biografia', validators=[Optional()])
    foto = FileField('Foto', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])
    linkedin_url = StringField('URL do LinkedIn', validators=[Optional(), URL()])
    palavras_chave = SelectMultipleField('Especialidades/Palavras-chave', 
                                        coerce=int,
                                        validators=[Optional()])
    submit = SubmitField('Salvar')

class BuscarPalestranteForm(FlaskForm):
    """Formulário para busca de palestrantes no LinkedIn"""
    palavras_chave = StringField('Palavras-chave (separadas por vírgula)', 
                                validators=[DataRequired()])
    min_seguidores = IntegerField('Mínimo de seguidores', validators=[Optional(), NumberRange(min=0)])
    localizacao = StringField('Localização', validators=[Optional()])
    max_resultados = IntegerField('Máximo de resultados', 
                                 validators=[Optional(), NumberRange(min=1, max=20)],
                                 default=10)
    submit = SubmitField('Buscar')

class PalavraChaveForm(FlaskForm):
    """Formulário para cadastro de palavras-chave/especialidades"""
    palavra = StringField('Palavra-chave', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Adicionar')