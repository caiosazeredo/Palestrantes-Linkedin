from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectMultipleField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class EventoForm(FlaskForm):
    """Formulário para cadastro e edição de eventos"""
    nome = StringField('Nome do evento', validators=[DataRequired(), Length(min=3, max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    data_inicio = DateTimeField('Data e hora de início', 
                               validators=[DataRequired()],
                               format='%Y-%m-%d %H:%M')
    data_fim = DateTimeField('Data e hora de término', 
                            validators=[DataRequired()],
                            format='%Y-%m-%d %H:%M')
    local = StringField('Local', validators=[DataRequired(), Length(max=100)])
    palestrantes = SelectMultipleField('Palestrantes', 
                                      coerce=int,
                                      validators=[Optional()])
    submit = SubmitField('Salvar')

class AvaliacaoForm(FlaskForm):
    """Formulário para avaliação de palestrantes em eventos"""
    nota = FloatField('Nota (0-10)', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message='A nota deve estar entre 0 e 10')
    ])
    comentario = TextAreaField('Comentário', validators=[Optional()])
    submit = SubmitField('Avaliar')