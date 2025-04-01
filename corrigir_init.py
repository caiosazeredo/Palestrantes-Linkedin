"""
Script para inicializar o banco de dados diretamente usando SQLAlchemy,
contornando o Flask-Migrate que está apresentando problemas.
"""
import os
import sys
import time

# Adicionar o diretório raiz ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar a aplicação
from app import create_app, db
from app.models.usuario import Usuario
from app.models.palestrante import Palestrante, PalavraChave
from app.models.evento import Evento, AvaliacaoPalestrante

def criar_banco_dados():
    print("Inicializando banco de dados diretamente com SQLAlchemy...")
    
    # Definir caminho do banco de dados em um local com permissões garantidas
    caminho_temp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    print(f"Usando caminho do banco de dados: {caminho_temp}")
    
    # Criar a aplicação com configuração personalizada
    class CustomConfig:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{caminho_temp}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'chave-de-desenvolvimento'
        UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    app = create_app(CustomConfig)
    
    with app.app_context():
        # Criar todas as tabelas definidas nos modelos
        print("Criando tabelas do banco de dados...")
        db.create_all()
        
        # Verificar se já existe um usuário administrador
        admin = Usuario.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("\nCriando usuário administrador padrão...")
            # Criar um usuário admin padrão
            admin = Usuario(
                nome="Administrador",
                email="admin@exemplo.com",
                is_admin=True
            )
            admin.set_senha("senha123")
            db.session.add(admin)
            
            # Commit das alterações
            db.session.commit()
            print("Usuário administrador criado com sucesso!")
            print("Email: admin@exemplo.com")
            print("Senha: senha123")
        else:
            print(f"\nUm usuário administrador já existe: {admin.nome} ({admin.email})")
        
        # Criar algumas palavras-chave de exemplo
        print("\nCriando algumas palavras-chave de exemplo...")
        palavras_chave_exemplos = [
            "Inteligência Artificial", "Data Science", "Machine Learning",
            "Python", "JavaScript", "Marketing Digital", "Design Thinking",
            "UX/UI", "Business Intelligence", "Empreendedorismo"
        ]
        
        for palavra in palavras_chave_exemplos:
            if not PalavraChave.query.filter_by(palavra=palavra).first():
                palavra_chave = PalavraChave(palavra=palavra)
                db.session.add(palavra_chave)
        
        # Commit final
        db.session.commit()
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    criar_banco_dados()
    
    print("\n==========================================================")
    print("Banco de dados inicializado com sucesso!")
    print("\nInformações de acesso:")
    print("- Email: admin@exemplo.com")
    print("- Senha: senha123")
    print("\nAgora você pode iniciar a aplicação com:")
    print("python executar_aplicacao.py")
    print("==========================================================")