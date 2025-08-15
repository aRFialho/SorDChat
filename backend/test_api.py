"""
Teste automatizado da API SorDChat
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:8001"


def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Testa um endpoint da API"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Método {method} não suportado")
            return None

        print(f"\n🧪 {description}")
        print(f"📡 {method.upper()} {endpoint}")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Sucesso!")
            try:
                result = response.json()
                if len(str(result)) > 200:
                    print("📄 Resposta: (dados recebidos)")
                else:
                    print(f"📄 Resposta: {json.dumps(result, indent=2)}")
                return result
            except:
                print("📄 Resposta: (não é JSON)")
                return response.text
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error = response.json()
                print(f"📄 Erro: {error}")
            except:
                print(f"📄 Erro: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"❌ Erro de conexão: Servidor não está rodando em {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None


def main():
    """Executa todos os testes"""
    print("🚀 Testando API SorDChat")
    print("=" * 50)

    # Teste 1: Página inicial
    test_endpoint("GET", "/", description="Teste da página inicial")

    # Teste 2: Health check
    test_endpoint("GET", "/health", description="Verificação de saúde")

    # Teste 3: Status
    test_endpoint("GET", "/status", description="Status do sistema")

    # Teste 4: Login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    login_result = test_endpoint(
        "POST",
        "/auth/login",
        data=login_data,
        description="Login do usuário admin"
    )

    if login_result and "access_token" in login_result:
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Teste 5: Informações do usuário
        test_endpoint(
            "GET",
            "/auth/me",
            headers=headers,
            description="Informações do usuário atual"
        )

        # Teste 6: Permissões
        test_endpoint(
            "GET",
            "/auth/permissions",
            headers=headers,
            description="Permissões do usuário"
        )

        # Teste 7: Logout
        test_endpoint(
            "POST",
            "/auth/logout",
            headers=headers,
            description="Logout do usuário"
        )

    else:
        print("\n⚠️ Não foi possível obter token. Pulando testes autenticados.")

    print("\n" + "=" * 50)
    print("🎉 Testes concluídos!")
    print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()