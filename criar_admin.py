"""
Script para criar um usuário administrador no sistema.
Substitui o uso do comando 'flask shell' para criar o usuário admin.
"""
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar as classes necessárias
from app import create_app, db
from app.models.usuario import Usuario

# Criar a aplicação
app = create_app()

# Usar o contexto da aplicação
with app.app_context():
    # Verificar se já existe um usuário administrador
    admin = Usuario.query.filter_by(is_admin=True).first()
    
    if admin:
        print(f"Um usuário administrador já existe: {admin.nome} ({admin.email})")
        criar_novo = input("Deseja criar outro administrador? (s/n): ").lower()
        
        if criar_novo != 's':
            print("Operação cancelada.")
            sys.exit(0)
    
    # Coletar informações do administrador
    print("\nCriando novo usuário administrador")
    print("==================================")
    
    nome = input("Nome completo: ")
    email = input("Email: ")
    senha = input("Senha: ")
    
    # Criar o usuário
    try:
        user = Usuario(nome=nome, email=email, is_admin=True)
        user.set_senha(senha)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\nUsuário administrador '{nome}' criado com sucesso!")
        print(f"Email: {email}")
        print(f"Você pode agora acessar o sistema com estas credenciais.")
        
    except Exception as e:
        db.session.rollback()
        print(f"\nErro ao criar usuário: {str(e)}")