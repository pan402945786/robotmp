# Prefer the project environment, then the existing Conda py311 environment.
$pythonPath = Join-Path $PSScriptRoot '.venv\python.exe'
$pythonArgs = @($args)
if (Test-Path -LiteralPath $pythonPath) {
    $pythonCommand = $pythonPath
} elseif (Get-Command conda -ErrorAction SilentlyContinue) {
    $pythonCommand = 'conda'
    $pythonArgs = @('run', '--no-capture-output', '-n', 'py311', 'python') + $pythonArgs
} else {
    throw 'Simulation environment missing. Create .venv from environment.yml or install Conda environment py311; see README.md.'
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($MyInvocation.ExpectingInput) {
        $input | & $pythonCommand @pythonArgs
    } else {
        & $pythonCommand @pythonArgs
    }
    $runExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $runExitCode
