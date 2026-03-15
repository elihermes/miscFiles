# Windows launcher for local web server
Set-Location -Path $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 run_server.py
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python run_server.py
}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 run_server.py
}
else {
    Write-Error "Python was not found in PATH."
    exit 1
}
