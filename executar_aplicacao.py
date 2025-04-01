"""
Script para executar a aplicação.
Substitui o comando 'flask run'.
"""
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar a aplicação
from app import create_app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    # Mostrar informações úteis
    print("\n============================================")
    print("Senac Cápsula - Gerenciamento de Palestrantes")
    print("============================================")
    print("\nIniciando servidor de desenvolvimento...")
    print("A aplicação estará disponível em: http://127.0.0.1:5000")
    print("Pressione CTRL+C para encerrar o servidor.")
    print("============================================\n")
    
    # Executar a aplicação em modo de desenvolvimento
    app.run(debug=True)