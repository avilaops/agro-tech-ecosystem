"""
Script para fechar automaticamente o Issue #1 (contratos de dados)
no agro-tech-ecosystem agora que os contratos foram implementados.

Usage:
    python scripts/close_issue_1.py
    
Requirements:
    - GitHub CLI (gh) instalado e autenticado
    - ou GITHUB_TOKEN environment variable
"""

import subprocess
import sys
import os


def close_issue_with_gh_cli():
    """Fecha o issue usando GitHub CLI."""
    try:
        # Verifica se gh está instalado
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        
        # Fecha o issue com comentário
        comment = """
✅ **CONCLUÍDO**

Contratos de dados implementados com sucesso:

## 📦 Entregáveis

- ✅ **contracts/precision.recommendations.schema.json** (v1.0.0)
  - Field zone analysis com recomendações agronômicas
  - Producer: Precision-Agriculture-Platform
  - Consumers: CanaSwarm-Intelligence, MicroGrid-Manager

- ✅ **contracts/telemetry.schema.json** (v1.0.0)
  - Telemetria em tempo real de robôs/drones
  - Producers: AgriBot-Retrofit, CanaSwarm-MicroBot, CanaSwarm-Core
  - Consumers: CanaSwarm-Swarm-Coordinator, Telemetry, Industrial-Automation-OS

- ✅ **contracts/vision.analysis.schema.json** (v1.0.0)
  - Resultados de análise de visão computacional
  - Producers: AI-Vision-Agriculture, CanaSwarm-Vision
  - Consumers: CanaSwarm-Intelligence, Precision-Agriculture-Platform

- ✅ **contracts/README.md**
  - Política de versionamento (SemVer)
  - Breaking change process (30-day notice, 90-day support)
  - Exemplos de validação (Python/Pydantic, JS/TypeScript)

## 🧪 Validação

- ✅ E2E test implementado: `integration/test_precision_to_intelligence.py`
- ✅ Teste passou: Precision → Intelligence data flow
- ✅ CI/CD configurado: `.github/workflows/e2e.yml` + `.github/workflows/contracts.yml`

## 🔄 Replicação

Contratos replicados para 4 repos em backlog:
- ✅ CanaSwarm-Docs (commit 6f93a45)
- ✅ Agro-Machinery-Marketplace (commit 1c64af7)
- ✅ Industrial-Automation-OS (commit b2280e0)
- ✅ CanaSwarm-3D-Models (commit f6e72ad)

---

**Commits:**
- agro-tech-ecosystem: `ab8fd03` [INTEGRATION] Data contracts + E2E test suite
- CanaSwarm-Docs: `6f93a45` [CONTRACTS] Add data contracts
- Agro-Machinery-Marketplace: `1c64af7` [CONTRACTS] Add data contracts
- Industrial-Automation-OS: `b2280e0` [CONTRACTS] Add data contracts
- CanaSwarm-3D-Models: `f6e72ad` [CONTRACTS] Add data contracts

**Status:** ✅ PRONTO PARA INTEGRAÇÃO
"""
        
        result = subprocess.run(
            ["gh", "issue", "close", "1", "-c", comment, "-R", "avilaops/agro-tech-ecosystem"],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ Issue #1 fechado com sucesso via GitHub CLI")
        print(f"   Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao fechar issue via gh CLI: {e}")
        print(f"   stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("⚠️  GitHub CLI (gh) não encontrado")
        return False


def close_issue_with_api():
    """Fecha o issue usando GitHub API diretamente."""
    try:
        import requests
        
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("❌ GITHUB_TOKEN não encontrado nas variáveis de ambiente")
            return False
        
        # Fecha o issue
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Adiciona comentário
        comment_url = "https://api.github.com/repos/avilaops/agro-tech-ecosystem/issues/1/comments"
        comment_data = {
            "body": """✅ **CONCLUÍDO**

Contratos de dados implementados:
- contracts/precision.recommendations.schema.json (v1.0.0)
- contracts/telemetry.schema.json (v1.0.0)
- contracts/vision.analysis.schema.json (v1.0.0)
- contracts/README.md (versioning policy)

E2E test validado: `integration/test_precision_to_intelligence.py`
CI/CD configurado: `.github/workflows/e2e.yml` + `contracts.yml`

Commit: ab8fd03"""
        }
        
        response = requests.post(comment_url, headers=headers, json=comment_data)
        response.raise_for_status()
        
        # Fecha o issue
        close_url = "https://api.github.com/repos/avilaops/agro-tech-ecosystem/issues/1"
        close_data = {"state": "closed"}
        
        response = requests.patch(close_url, headers=headers, json=close_data)
        response.raise_for_status()
        
        print("✅ Issue #1 fechado com sucesso via GitHub API")
        return True
        
    except ImportError:
        print("❌ Biblioteca 'requests' não encontrada (pip install requests)")
        return False
    except Exception as e:
        print(f"❌ Erro ao fechar issue via API: {e}")
        return False


def main():
    print("🔄 Fechando Issue #1 no agro-tech-ecosystem...")
    print()
    
    # Tenta primeiro com gh CLI (mais fácil)
    if close_issue_with_gh_cli():
        return 0
    
    # Se falhar, tenta com API
    print("\n🔄 Tentando via GitHub API...")
    if close_issue_with_api():
        return 0
    
    # Se ambos falharem, instrui usuário
    print("\n" + "="*80)
    print("⚠️  Não foi possível fechar automaticamente")
    print("="*80)
    print("\nPara fechar manualmente, escolha uma opção:\n")
    print("1️⃣  Via GitHub CLI:")
    print("   gh issue close 1 -R avilaops/agro-tech-ecosystem -c 'Contratos implementados'")
    print("\n2️⃣  Via Web:")
    print("   https://github.com/avilaops/agro-tech-ecosystem/issues/1")
    print("\n3️⃣  Via API:")
    print("   curl -X PATCH https://api.github.com/repos/avilaops/agro-tech-ecosystem/issues/1 \\")
    print("     -H 'Authorization: token YOUR_TOKEN' \\")
    print("     -d '{\"state\":\"closed\"}'")
    print()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
