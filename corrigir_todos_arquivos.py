"""
Script para identificar e corrigir todos os arquivos .py com problemas de codificação.
Versão 2.0 - Com suporte para corrigir o arquivo usuario.py
"""
import os
import sys

def verificar_codificacao_arquivo(caminho):
    """Verifica se o arquivo pode ser lido com codificação UTF-8"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False

def corrigir_arquivo(arquivo_path, conteudo_correto=None):
    """Corrige um arquivo com problema de codificação"""
    print(f"\nVerificando arquivo: {arquivo_path}")
    
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_path):
        print(f"ERRO: O arquivo {arquivo_path} não existe.")
        return False
    
    # Se não foi fornecido conteúdo correto, tente adivinhar qual arquivo é
    if conteudo_correto is None:
        nome_arquivo = os.path.basename(arquivo_path)
        diretorio = os.path.dirname(arquivo_path)
        
        if nome_arquivo == '__init__.py' and diretorio == 'app':
            conteudo_correto = gerar_conteudo_init()
        elif nome_arquivo == 'config.py':
            conteudo_correto = gerar_conteudo_config()
        elif nome_arquivo == 'usuario.py' and 'models' in diretorio:
            conteudo_correto = gerar_conteudo_usuario()
        else:
            print(f"Não há conteúdo definido para {nome_arquivo} em {diretorio}.")
            return False
    
    # Criar backup do arquivo antes de substituir
    backup_path = arquivo_path + '.bak'
    try:
        with open(arquivo_path, 'rb') as f_read:
            conteudo_bytes = f_read.read()
        
        with open(backup_path, 'wb') as f_backup:
            f_backup.write(conteudo_bytes)
        
        print(f"Backup criado em: {backup_path}")
    except Exception as e:
        print(f"Aviso: Não foi possível criar backup: {str(e)}")
    
    # Escrever novo conteúdo
    try:
        with open(arquivo_path, 'w', encoding='utf-8') as f_write:
            f_write.write(conteudo_correto)
        
        print(f"Arquivo {arquivo_path} corrigido com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO ao corrigir {arquivo_path}: {str(e)}")
        return False

def gerar_conteudo_init():
    """Gera o conteúdo correto para o arquivo __init__.py"""
    return '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
import os

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Por favor, faça login para acessar esta página.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    # Criar diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Registrar blueprints
    from app.controllers.auth import bp as auth_bp
    from app.controllers.palestrantes import bp as palestrantes_bp
    from app.controllers.eventos import bp as eventos_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(palestrantes_bp, url_prefix='/palestrantes')
    app.register_blueprint(eventos_bp, url_prefix='/eventos')
    
    # Definir rota principal
    from app.controllers import main
    app.register_blueprint(main.bp)
    
    return app
'''

def gerar_conteudo_config():
    """Gera o conteúdo correto para o arquivo config.py"""
    return '''import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-desenvolvimento'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\
        'sqlite:///' + os.path.join(basedir, '../instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações para o crawler do LinkedIn
    LINKEDIN_USERNAME = os.environ.get('LINKEDIN_USERNAME')
    LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD')
    
    # Configurações para upload de arquivos
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
'''

def gerar_conteudo_usuario():
    """Gera o conteúdo correto para o arquivo usuario.py"""
    return '''from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_senha(self, senha):
        """Define a senha criptografada para o usuário"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

@login.user_loader
def load_user(id):
    """Função necessária para o Flask-Login carregar o usuário da sessão"""
    return Usuario.query.get(int(id))
'''

def verificar_todos_arquivos_python():
    """Verifica todos os arquivos .py no projeto"""
    arquivos_com_problemas = []
    
    # Verificar diretório atual e todos os subdiretórios
    for pasta_atual, subpastas, arquivos in os.walk('.'):
        for arquivo in arquivos:
            if arquivo.endswith('.py'):
                caminho_completo = os.path.join(pasta_atual, arquivo)
                
                # Ignorar arquivos da pasta venv ou env
                if 'venv' in caminho_completo or '/env/' in caminho_completo or '\\env\\' in caminho_completo:
                    continue
                
                # Verificar codificação
                if not verificar_codificacao_arquivo(caminho_completo):
                    arquivos_com_problemas.append(caminho_completo)
    
    return arquivos_com_problemas

def main():
    print("Verificando arquivos Python com problemas de codificação...\n")
    
    # Encontrar todos os arquivos com problemas
    arquivos_com_problemas = verificar_todos_arquivos_python()
    
    if not arquivos_com_problemas:
        print("Não foram encontrados arquivos com problemas de codificação.")
        return
    
    print(f"Encontrados {len(arquivos_com_problemas)} arquivos com problemas:")
    for idx, arquivo in enumerate(arquivos_com_problemas, 1):
        print(f"{idx}. {arquivo}")
    
    print("\nDeseja corrigir todos os arquivos? (s/n): ", end="")
    resposta = input().lower()
    
    if resposta != 's':
        print("Operação cancelada.")
        return
    
    # Corrigir cada arquivo encontrado
    arquivos_corrigidos = 0
    arquivos_nao_corrigidos = []
    
    for arquivo in arquivos_com_problemas:
        if corrigir_arquivo(arquivo):
            arquivos_corrigidos += 1
        else:
            arquivos_nao_corrigidos.append(arquivo)
    
    print(f"\n{arquivos_corrigidos} de {len(arquivos_com_problemas)} arquivos foram corrigidos.")
    
    if arquivos_nao_corrigidos:
        print("\nOs seguintes arquivos NÃO foram corrigidos automaticamente:")
        for arq in arquivos_nao_corrigidos:
            print(f"- {arq}")
        print("\nVocê precisará corrigir estes arquivos manualmente.")
    
    print("\nAgora você pode tentar inicializar o banco de dados novamente com:")
    print("python inicializar_db.py")

if __name__ == "__main__":
    main()