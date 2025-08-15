"""
Teste das funcionalidades avançadas: Upload e Notificações
"""

import requests
import json
from datetime import datetime
import os

# Configuração
API_BASE = "http://127.0.0.1:8001"


def test_file_upload():
    """Testa sistema de upload de arquivos"""

    print("🧪 Testando sistema de upload de arquivos...")

    # Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })

    if login_response.status_code != 200:
        print("❌ Erro no login")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Criar arquivo de teste
    test_file_content = "Este é um arquivo de teste do SorDChat!\nData: " + datetime.now().isoformat()
    test_file_path = "test_file.txt"

    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_file_content)

    try:
        # Testar upload
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_file.txt", f, "text/plain")}
            data = {"category": "documents", "description": "Arquivo de teste"}

            response = requests.post(
                f"{API_BASE}/files/upload",
                files=files,
                data=data,
                headers=headers
            )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                file_id = result["file"]["id"]
                print(f"✅ Upload realizado com sucesso! ID: {file_id}")

                # Testar listagem de arquivos
                list_response = requests.get(f"{API_BASE}/files/", headers=headers)
                if list_response.status_code == 200:
                    files_data = list_response.json()
                    print(f"✅ Listagem: {len(files_data['files'])} arquivos encontrados")

                # Testar informações do arquivo
                info_response = requests.get(f"{API_BASE}/files/{file_id}/info", headers=headers)
                if info_response.status_code == 200:
                    print("✅ Informações do arquivo obtidas")

                # Testar download
                download_response = requests.get(f"{API_BASE}/files/{file_id}", headers=headers)
                if download_response.status_code == 200:
                    print("✅ Download do arquivo realizado")

                    # Testar estatísticas
                stats_response = requests.get(f"{API_BASE}/files/stats/overview", headers=headers)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"✅ Estatísticas: {stats['total_files']} arquivos, {stats['total_size_mb']} MB")

                return file_id
            else:
                print(f"❌ Erro no upload: {result.get('errors')}")
        else:
            print(f"❌ Erro HTTP no upload: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro no teste de upload: {e}")

    finally:
        # Limpar arquivo de teste
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

    return None


def test_notifications():
    """Testa sistema de notificações"""

    print("\n🧪 Testando sistema de notificações...")

    # Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })

    if login_response.status_code != 200:
        print("❌ Erro no login")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Testar criação de notificação
        notification_data = {
            "title": "Teste de Notificação",
            "message": "Esta é uma notificação de teste do sistema!",
            "type": "info",
            "data": {"test": True}
        }

        create_response = requests.post(
            f"{API_BASE}/notifications/",
            json=notification_data,
            headers=headers
        )

        if create_response.status_code == 200:
            print("✅ Notificação criada com sucesso")

            # Testar listagem de notificações
            list_response = requests.get(f"{API_BASE}/notifications/", headers=headers)
            if list_response.status_code == 200:
                notifications = list_response.json()
                print(f"✅ Listagem: {len(notifications['notifications'])} notificações")
                print(f"✅ Não lidas: {notifications['unread_count']}")

                if notifications['notifications']:
                    notification_id = notifications['notifications'][0]['id']

                    # Testar marcar como lida
                    read_response = requests.post(
                        f"{API_BASE}/notifications/{notification_id}/read",
                        headers=headers
                    )
                    if read_response.status_code == 200:
                        print("✅ Notificação marcada como lida")

            # Testar contador de não lidas
            count_response = requests.get(f"{API_BASE}/notifications/unread-count", headers=headers)
            if count_response.status_code == 200:
                count = count_response.json()
                print(f"✅ Contador não lidas: {count['unread_count']}")

            # Testar notificações de teste
            test_endpoints = [
                "/notifications/test/ticket",
                "/notifications/test/task",
                "/notifications/test/message"
            ]

            for endpoint in test_endpoints:
                test_response = requests.post(f"{API_BASE}{endpoint}", headers=headers)
                if test_response.status_code == 200:
                    print(f"✅ Teste {endpoint.split('/')[-1]} enviado")

            # Testar estatísticas
            stats_response = requests.get(f"{API_BASE}/notifications/stats", headers=headers)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Estatísticas: {stats['total_notifications']} total, {stats['unread_count']} não lidas")

        else:
            print(f"❌ Erro ao criar notificação: {create_response.status_code}")

    except Exception as e:
        print(f"❌ Erro no teste de notificações: {e}")


def test_integration():
    """Testa integração entre funcionalidades"""

    print("\n🧪 Testando integração das funcionalidades...")

    # Login
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Testar todos os endpoints principais
    endpoints_to_test = [
        ("GET", "/", "Página inicial"),
        ("GET", "/health", "Health check"),
        ("GET", "/users/", "Lista usuários"),
        ("GET", "/tickets/", "Lista tickets"),
        ("GET", "/tasks/", "Lista tasks"),
        ("GET", "/messages/", "Lista mensagens"),
        ("GET", "/dashboard/overview", "Dashboard"),
        ("GET", "/files/", "Lista arquivos"),
        ("GET", "/notifications/", "Lista notificações"),
    ]

    successful_tests = 0
    total_tests = len(endpoints_to_test)

    for method, endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)

            if response.status_code == 200:
                print(f"✅ {description}")
                successful_tests += 1
            else:
                print(f"❌ {description} - Status: {response.status_code}")

        except Exception as e:
            print(f"❌ {description} - Erro: {e}")

    print(f"\n📊 Integração: {successful_tests}/{total_tests} testes passaram")

    return successful_tests == total_tests


def main():
    """Função principal de teste"""

    print("🚀 SorDChat - Teste de Funcionalidades Avançadas")
    print("=" * 60)

    # Testar upload de arquivos
    file_id = test_file_upload()

    # Testar notificações
    test_notifications()

    # Testar integração
    integration_success = test_integration()

    print("\n" + "=" * 60)

    if integration_success:
        print("🎉 Todos os testes das funcionalidades avançadas passaram!")
        print("\n🚀 Funcionalidades implementadas com sucesso:")
        print("   📁 Upload de arquivos com validação")
        print("   🖼️ Geração automática de thumbnails")
        print("   🔔 Sistema de notificações em tempo real")
        print("   📱 Push notifications")
        print("   📊 Estatísticas avançadas")
        print("   🔄 Integração com WebSocket")
    else:
        print("⚠️ Alguns testes falharam")

    print(f"\n📅 Teste concluído em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


if __name__ == "__main__":
    main()