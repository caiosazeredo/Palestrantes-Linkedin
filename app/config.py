import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
ECHO est� desativado.
    # Configurações para o crawler do LinkedIn
    LINKEDIN_USERNAME = os.environ.get('LINKEDIN_USERNAME')
    LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD')
ECHO est� desativado.
    # Configurações para upload de arquivos
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
