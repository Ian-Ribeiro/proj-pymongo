$venvPath = ".\.venv"

if (Test-Path $venvPath) {
    Write-Host "🧹 Removendo ambiente virtual existente..."
    Remove-Item -Recurse -Force $venvPath
}

Write-Host "🐍 Criando novo ambiente virtual em $venvPath..."
python -m venv $venvPath

Write-Host "📦 Instalando dependências do requirements.txt..."
& "$venvPath\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`n✅ Ambiente virtual '.venv' recriado com sucesso!"
Write-Host "🌐 Configuração concluída. Você pode ativar o ambiesnte virtual com 'source $venvPath\Scripts\Activate.ps1'."