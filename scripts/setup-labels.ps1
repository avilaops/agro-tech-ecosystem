# Script para criar labels padronizadas em todos os repositórios
# Uso: .\setup-labels.ps1

$repos = @(
    "avilaops/agro-tech-ecosystem",
    "avilaops/Precision-Agriculture-Platform",
    "avilaops/CanaSwarm-Intelligence",
    "avilaops/AgriBot-Retrofit",
    "avilaops/AI-Vision-Agriculture",
    "avilaops/CanaSwarm-Core",
    "avilaops/CanaSwarm-MicroBot",
    "avilaops/CanaSwarm-Vision",
    "avilaops/CanaSwarm-Swarm-Coordinator",
    "avilaops/CanaSwarm-3D-Models",
    "avilaops/CanaSwarm-Solar-Manager",
    "avilaops/CanaSwarm-Docs",
    "avilaops/MicroGrid-Manager",
    "avilaops/Industrial-Automation-OS",
    "avilaops/Robotics-Swarm-Simulator",
    "avilaops/Autonomous-Agent-Framework",
    "avilaops/Agro-Machinery-Marketplace"
)

# Definir labels (nome, cor, descrição)
$labels = @(
    # TYPE
    @{name="demand"; color="FF6B6B"; description="Demanda de mercado/cliente"},
    @{name="feature"; color="4ECDC4"; description="Nova funcionalidade"},
    @{name="bug"; color="EE5A6F"; description="Correção de bug"},
    @{name="refactor"; color="95E1D3"; description="Refatoração"},
    @{name="docs"; color="A8E6CF"; description="Documentação"},
    @{name="infra"; color="FFD3B6"; description="Infraestrutura/DevOps"},
    @{name="research"; color="FFAAA5"; description="Pesquisa/spike"},
    
    # LAYER
    @{name="layer:decision"; color="667BC6"; description="Analytics, ROI, recomendações"},
    @{name="layer:sensing"; color="DA7F8F"; description="Visão, sensores, ingest"},
    @{name="layer:execution"; color="FADA7A"; description="Máquinas, robôs, atuação"},
    @{name="layer:infra"; color="A4D0A4"; description="APIs, dados, energia, DevOps"},
    
    # PRIORITY
    @{name="P0"; color="D32F2F"; description="Bloqueador / Cliente pagante esperando"},
    @{name="P1"; color="F57C00"; description="Importante / Impacto alto / Roadmap Q"},
    @{name="P2"; color="FBC02D"; description="Útil / Pode esperar Q+1"},
    @{name="P3"; color="9E9E9E"; description="Nice-to-have / Backlog"},
    
    # STATUS
    @{name="triage"; color="BDBDBD"; description="Precisa ser analisado"},
    @{name="blocked"; color="E91E63"; description="Bloqueado por dependência"},
    @{name="ready"; color="00C853"; description="Spec pronta, pode começar"},
    @{name="in-progress"; color="2196F3"; description="Sendo desenvolvido"},
    @{name="in-review"; color="9C27B0"; description="PR aberto, aguardando review"},
    @{name="done"; color="4CAF50"; description="Completo"},
    
    # QUARTER
    @{name="Q1-2026"; color="81C784"; description="Jan-Mar 2026"},
    @{name="Q2-2026"; color="64B5F6"; description="Abr-Jun 2026"},
    @{name="Q3-2026"; color="FFB74D"; description="Jul-Set 2026"},
    @{name="Q4-2026"; color="E57373"; description="Out-Dez 2026"},
    
    # EFFORT
    @{name="effort:XS"; color="E8F5E9"; description="< 1 dia"},
    @{name="effort:S"; color="C8E6C9"; description="1-3 dias"},
    @{name="effort:M"; color="A5D6A7"; description="1 semana"},
    @{name="effort:L"; color="81C784"; description="2-4 semanas"},
    @{name="effort:XL"; color="66BB6A"; description="1-3 meses"},
    
    # IMPACT
    @{name="impact:high"; color="D32F2F"; description="Crítico para MVP ou cliente pagante"},
    @{name="impact:medium"; color="FBC02D"; description="Melhora significativa"},
    @{name="impact:low"; color="9E9E9E"; description="Incremental"},
    
    # REPO (para o project central cross-repo)
    @{name="repo:precision-platform"; color="E3F2FD"; description="Precision-Agriculture-Platform"},
    @{name="repo:canaswarm-intelligence"; color="F3E5F5"; description="CanaSwarm-Intelligence"},
    @{name="repo:agribot-retrofit"; color="FFF3E0"; description="AgriBot-Retrofit"},
    @{name="repo:ai-vision"; color="EDE7F6"; description="AI-Vision-Agriculture"},
    @{name="repo:microbot"; color="E0F2F1"; description="CanaSwarm-MicroBot"},
    @{name="repo:swarm-coordinator"; color="FCE4EC"; description="Swarm-Coordinator"},
    @{name="repo:solar-manager"; color="FFF9C4"; description="Solar-Manager"},
    @{name="repo:microgrid-manager"; color="F1F8E9"; description="MicroGrid-Manager"},
    @{name="repo:marketplace"; color="E1F5FE"; description="Agro-Machinery-Marketplace"},
    @{name="repo:multiple"; color="CFD8DC"; description="Afeta múltiplos repos"}
)

Write-Host "`n🏷️  SETUP DE LABELS PADRONIZADAS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$totalRepos = $repos.Count
$current = 0

foreach ($repo in $repos) {
    $current++
    Write-Host "[$current/$totalRepos] Processando: $repo" -ForegroundColor Yellow
    
    foreach ($label in $labels) {
        $name = $label.name
        $color = $label.color
        $description = $label.description
        
        # Tentar criar a label (ignora erro se já existe)
        try {
            gh label create $name --color $color --description $description --repo $repo 2>$null
            Write-Host "  ✅ Criada: $name" -ForegroundColor Green
        } catch {
            # Label já existe, tentar atualizar
            try {
                gh label edit $name --color $color --description $description --repo $repo 2>$null
                Write-Host "  🔄 Atualizada: $name" -ForegroundColor Blue
            } catch {
                Write-Host "  ⚠️  Erro: $name" -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
}

Write-Host "`n✅ LABELS APLICADAS EM TODOS OS REPOS!" -ForegroundColor Green
Write-Host "`nTotal de labels: $($labels.Count)" -ForegroundColor Cyan
Write-Host "Total de repos: $totalRepos`n" -ForegroundColor Cyan
