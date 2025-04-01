"""
Script para executar a aplicação usando um banco de dados SQLite em memória.
Isso evita problemas de permissão de acesso a arquivos.
"""
import os
import sys

# Adicionar o diretório raiz ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar a aplicação
from app import create_app, db
from app.models.usuario import Usuario
from app.models.palestrante import Palestrante, PalavraChave
from app.models.evento import Evento, AvaliacaoPalestrante

# Configuração para banco de dados em memória
class InMemoryConfig:
    # Usando SQLite em memória
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'chave-secreta-desenvolvimento'
    
    # Configurações para o crawler do LinkedIn (não usadas neste caso)
    LINKEDIN_USERNAME = 'user@example.com'
    LINKEDIN_PASSWORD = 'password'
    
    # Configurações para upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Criar a aplicação com a configuração em memória
app = create_app(InMemoryConfig)

# Inicializar e popular o banco de dados em memória
def inicializar_banco_dados():
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Criar usuário administrador
        admin = Usuario(
            nome="Administrador",
            email="admin@exemplo.com",
            is_admin=True
        )
        admin.set_senha("senha123")
        db.session.add(admin)
        
        # Criar usuário comum
        usuario = Usuario(
            nome="Usuário Teste",
            email="usuario@exemplo.com",
            is_admin=False
        )
        usuario.set_senha("senha123")
        db.session.add(usuario)
        
        # Criar algumas palavras-chave
        palavras_chave = [
            "Inteligência Artificial", "Machine Learning", "Python", 
            "JavaScript", "Marketing Digital", "Design", "UX/UI", 
            "Business Intelligence", "Empreendedorismo", "Inovação"
        ]
        
        for palavra in palavras_chave:
            db.session.add(PalavraChave(palavra=palavra))
        
        # Commit para salvar os dados
        db.session.commit()
        
        print("Banco de dados em memória inicializado com sucesso!")
        print("\nUsuários para teste:")
        print("- Admin: admin@exemplo.com / senha123")
        print("- Usuário: usuario@exemplo.com / senha123")

if __name__ == "__main__":
    # Inicializar banco de dados em memória
    inicializar_banco_dados()
    
    # Executar a aplicação
    print("\n============================================")
    print("Senac Cápsula - Gerenciamento de Palestrantes")
    print("============================================")
    print("MODO DE TESTE COM BANCO DE DADOS EM MEMÓRIA")
    print("Note que os dados serão perdidos ao reiniciar a aplicação")
    print("\nIniciando servidor de desenvolvimento...")
    print("A aplicação estará disponível em: http://127.0.0.1:5000")
    print("Pressione CTRL+C para encerrar o servidor.")
    print("============================================\n")
    
    # Executar a aplicação em modo de desenvolvimento
    app.run(debug=True)