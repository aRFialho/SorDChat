"""
Script para criar usuário de teste
"""

import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import sys

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.auth import get_password_hash

load_dotenv()


def create_test_user():
    """Cria usuário de teste com senha criptografada"""

    database_url = os.getenv("DATABASE_URL")
    parsed = urlparse(database_url)

    conn = psycopg2.connect(
        host=parsed.hostname,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password,
        port=parsed.port or 5432
    )

    cursor = conn.cursor()

    try:
        # Senha para o usuário admin
        admin_password = "admin123"
        admin_hash = get_password_hash(admin_password)

        # Atualizar o usuário admin existente
        cursor.execute("""
                       UPDATE users
                       SET hashed_password = %s,
                           email           = %s,
                           full_name       = %s
                       WHERE username = 'admin'
                       """, (admin_hash, "admin@sordchat.com", "Administrador Master"))

        # Criar usuário coordenador de teste
        coord_password = "coord123"
        coord_hash = get_password_hash(coord_password)

        cursor.execute("""
                       INSERT INTO users (username, email, full_name, hashed_password, department, access_level)
                       VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO
                       UPDATE SET
                           hashed_password = EXCLUDED.hashed_password,
                           email = EXCLUDED.email,
                           full_name = EXCLUDED.full_name
                       """, ("coordenador", "coord@sordchat.com", "João Coordenador", coord_hash, "TI", "coordenador"))

        # Criar usuário padrão de teste
        user_password = "user123"
        user_hash = get_password_hash(user_password)

        cursor.execute("""
                       INSERT INTO users (username, email, full_name, hashed_password, department, access_level)
                       VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO
                       UPDATE SET
                           hashed_password = EXCLUDED.hashed_password,
                           email = EXCLUDED.email,
                           full_name = EXCLUDED.full_name
                       """, ("usuario", "user@sordchat.com", "Maria Usuária", user_hash, "Vendas", "padrao"))

        conn.commit()

        print("✅ Usuários de teste criados com sucesso!")
        print("\n👥 Usuários disponíveis:")
        print("1. admin / admin123 (Master)")
        print("2. coordenador / coord123 (Coordenador)")
        print("3. usuario / user123 (Padrão)")

    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_test_user()