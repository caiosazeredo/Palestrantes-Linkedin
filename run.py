from app import create_app, db
from app.models.usuario import Usuario
from app.models.palestrante import Palestrante, PalavraChave
from app.models.evento import Evento, AvaliacaoPalestrante

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Disponibiliza variáveis para o shell Flask"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Palestrante': Palestrante,
        'PalavraChave': PalavraChave,
        'Evento': Evento,
        'AvaliacaoPalestrante': AvaliacaoPalestrante
    }

if __name__ == '__main__':
    app.run(debug=True)
