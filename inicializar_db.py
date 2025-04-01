"""
Script para inicializar o banco de dados do sistema de Palestrantes Senac Cápsula.
Este script substitui os comandos 'flask db init', 'flask db migrate' e 'flask db upgrade'.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade

# Importar a aplicação - ajuste o caminho conforme a estrutura do seu projeto
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar a função create_app do seu projeto
from app import create_app, db

# Criar a aplicação
app = create_app()

# Usar o contexto da aplicação
with app.app_context():
    # Verificar se a pasta migrations já existe
    if not os.path.exists('migrations'):
        print("Inicializando o repositório de migrações...")
        init()
    
    print("Criando nova migração...")
    migrate(message="Inicialização do banco de dados")
    
    print("Aplicando a migração...")
    upgrade()
    
    print("Banco de dados inicializado com sucesso!")

print("\nPróximo passo: Execute 'python criar_admin.py' para criar um usuário administrador")