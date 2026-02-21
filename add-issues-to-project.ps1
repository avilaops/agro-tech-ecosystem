$env:GITHUB_TOKEN = $null

$projectId = "PVT_kwHODkuP_c4BPuev"

# Array de issues (owner/repo#number)
$issues = @(
  "avilaops/agro-tech-ecosystem#5",
  "avilaops/agro-tech-ecosystem#2",
  "avilaops/agro-tech-ecosystem#3",
  "avilaops/agro-tech-ecosystem#4",
  "avilaops/CanaSwarm-Intelligence#2",
  "avilaops/CanaSwarm-Intelligence#3"
)

$success = 0
$failed = 0
$skipped = 0

foreach ($issue in $issues) {
  $parts = $issue -split "/"
  $owner = $parts[0]
  $repoAndNumber = $parts[1] -split "#"
  $repo = $repoAndNumber[0]
  $number = [int]$repoAndNumber[1]
  
  Write-Host ""
  Write-Host "Processando: $issue" -ForegroundColor Cyan
  
  # Pega o node ID do issue
  $query = "query { repository(owner: \`"$owner\`", name: \`"$repo\`") { issue(number: $number) { id title } } }"
  
  try {
    $result = gh api graphql -f query="$query" | ConvertFrom-Json
    $issueId = $result.data.repository.issue.id
    $title = $result.data.repository.issue.title
    
    Write-Host "  Issue ID: $issueId" -ForegroundColor Gray
    Write-Host "  Título: $title" -ForegroundColor Gray
    
    # Adiciona ao projeto
    $mutation = "mutation { addProjectV2ItemById(input: {projectId: \`"$projectId\`", contentId: \`"$issueId\`"}) { item { id } } }"
    
    $addResult = gh api graphql -f query="$mutation" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
      Write-Host "  ✅ Adicionado ao projeto #7" -ForegroundColor Green
      $success++
    } else {
      # Verifica se já estava no projeto
      if ($addResult -match "already exists") {
        Write-Host "  ℹ️ Já estava no projeto" -ForegroundColor Blue
        $skipped++
      } else {
        Write-Host "  ⚠️ Erro: $addResult" -ForegroundColor Yellow
        $failed++
      }
    }
    
  } catch {
    Write-Host "  ⚠️ Erro: $_" -ForegroundColor Red
    $failed++
  }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "✅ Adicionados: $success issues" -ForegroundColor Green
Write-Host "ℹ️ Já existiam: $skipped issues" -ForegroundColor Blue
Write-Host "⚠️ Falhas: $failed issues" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "🔗 Ver projeto: https://github.com/users/avilaops/projects/7" -ForegroundColor Cyan
