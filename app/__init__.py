from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
import os

# Inicializar extens√µes
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor, fa√ßa login para acessar esta p√°gina.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
ECHO est† desativado.
    # Inicializar extens√µes com a aplica√ß√£o
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
ECHO est† desativado.
    # Criar diret√≥rio de uploads se n√£o existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ECHO est† desativado.
    # Registrar blueprints
    from app.controllers.auth import bp as auth_bp
    from app.controllers.palestrantes import bp as palestrantes_bp
    from app.controllers.eventos import bp as eventos_bp
ECHO est† desativado.
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(palestrantes_bp, url_prefix='/palestrantes')
    app.register_blueprint(eventos_bp, url_prefix='/eventos')
ECHO est† desativado.
    # Definir rota principal
    from app.controllers import main
    app.register_blueprint(main.bp)
ECHO est† desativado.
    return app
