import json
import os

import requests

TOKEN = os.getenv("PORTAL_TRANSPARENCIA_TOKEN")


def obter_headers():
    if not TOKEN:
        raise RuntimeError(
            "Defina a variável de ambiente PORTAL_TRANSPARENCIA_TOKEN antes de executar busca_api.py."
        )
    return {
        "chave-api-dados": TOKEN,
        "Accept": "application/json",
    }

def testar_formato_exato():
    """
    Testa o formato exato do e-mail
    """
    # Formato 1: Como está no e-mail (array com objeto)
    headers = obter_headers()
    
    print("🔍 TESTANDO COM O FORMATO EXATO DO E-MAIL")
    print("="*60)
    print(f"Headers: {headers}")
    print("="*60)
    
    # Endpoints para testar
    endpoints = [
        "http://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi",
        "http://api.portaldatransparencia.gov.br/api-de-dados/emendas",
        "http://api.portaldatransparencia.gov.br/api-de-dados/transferencias/especiais",
        "http://api.portaldatransparencia.gov.br/api-de-dados/emendas/por-nome-parlamentar?nome=NIKOLAS%20FERREIRA"
    ]
    
    for url in endpoints:
        print(f"\n📌 Testando: {url}")
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params={"pagina": 1},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ FUNCIONOU!")
                dados = response.json()
                if isinstance(dados, list):
                    print(f"   Registros: {len(dados)}")
                    if len(dados) > 0:
                        print(f"   Primeiro: {json.dumps(dados[0], indent=2, ensure_ascii=False)[:200]}")
                else:
                    print(f"   Resposta: {str(dados)[:200]}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                if response.text:
                    print(f"   Mensagem: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Exceção: {e}")

def testar_com_accept_header():
    """
    Testa adicionando o header Accept como no exemplo Java
    """
    headers = obter_headers()
    
    print("\n" + "="*60)
    print("🔍 TESTANDO COM HEADER ACCEPT (como no Java)")
    print("="*60)
    
    url = "http://api.portaldatransparencia.gov.br/api-de-dados/emendas"
    
    try:
        response = requests.get(url, headers=headers, params={"pagina": 1})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            dados = response.json()
            print(f"Registros: {len(dados)}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    testar_formato_exato()
    testar_com_accept_header()
