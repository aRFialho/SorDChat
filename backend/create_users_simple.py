"""
Script simplificado para criar usuários de teste
"""

import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()


def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_test_users():
    """Cria usuários de teste"""

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
        print("🔨 Criando usuários de teste...")

        # Usuário admin (Master)
        admin_hash = hash_password("admin123")
        cursor.execute("""
                       UPDATE users
                       SET hashed_password = %s,
                           email           = %s,
                           full_name       = %s
                       WHERE username = 'admin'
                       """, (admin_hash, "admin@sordchat.com", "Administrador Master"))

        # Usuário coordenador
        coord_hash = hash_password("coord123")
        cursor.execute("""
                       INSERT INTO users (username, email, full_name, hashed_password, department, access_level)
                       VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO
                       UPDATE SET
                           hashed_password = EXCLUDED.hashed_password,
                           email = EXCLUDED.email,
                           full_name = EXCLUDED.full_name,
                           department = EXCLUDED.department
                       """, ("coordenador", "coord@sordchat.com", "João Coordenador", coord_hash, "TI", "coordenador"))

        # Usuário padrão
        user_hash = hash_password("user123")
        cursor.execute("""
                       INSERT INTO users (username, email, full_name, hashed_password, department, access_level)
                       VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO
                       UPDATE SET
                           hashed_password = EXCLUDED.hashed_password,
                           email = EXCLUDED.email,
                           full_name = EXCLUDED.full_name,
                           department = EXCLUDED.department
                       """, ("usuario", "user@sordchat.com", "Maria Usuária", user_hash, "Vendas", "padrao"))

        conn.commit()

        print("✅ Usuários de teste criados com sucesso!")
        print("\n👥 Credenciais de acesso:")
        print("┌─────────────┬─────────────┬─────────────────┐")
        print("│ Username    │ Password    │ Nível           │")
        print("├─────────────┼─────────────┼─────────────────┤")
        print("│ admin       │ admin123    │ Master          │")
        print("│ coordenador │ coord123    │ Coordenador     │")
        print("│ usuario     │ user123     │ Padrão          │")
        print("└─────────────┴─────────────┴─────────────────┘")

    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_test_users()