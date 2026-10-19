# Forward Python arguments to this repository's simulation environment.
$pythonPath = Join-Path $PSScriptRoot '.venv\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Simulation environment missing. Create .venv from environment.yml first; see README.md.'
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($MyInvocation.ExpectingInput) {
        $input | & $pythonPath @args
    } else {
        & $pythonPath @args
    }
    $runExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $runExitCode
