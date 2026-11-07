
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$env:Path = "$root;$env:Path"

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logPath = Join-Path $PSScriptRoot "harness-run-$timestamp.txt"

$script:results = [System.Collections.Generic.List[object]]::new()

Start-Transcript -Path $logPath -Force | Out-Null

function Invoke-Gate {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host "`n========== $Name ==========" -ForegroundColor Cyan

    $code = 1

      $previousErrorActionPreference = $ErrorActionPreference

    try {
        # Native tools may write informational messages to stderr.
        # Do not treat stderr alone as a terminating PowerShell error.
        $ErrorActionPreference = 'Continue'

        $output = & $Action 2>&1

        # Read the actual native command exit code immediately.
        $code = $LASTEXITCODE

        # Preserve command output in the transcript.
        $output | ForEach-Object {
            Write-Host "$_"
        }

        if ($null -eq $code) {
            $code = 0
        }
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $code = 1
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    $status = if ($code -eq 0) { 'PASS' } else { 'FAIL' }

    Write-Host "$Name : $status (exit code $code)" -ForegroundColor $(if ($code -eq 0) { 'Green' } else { 'Red' })

    $script:results.Add([PSCustomObject]@{
        Gate     = $Name
        Status   = $status
        ExitCode = $code
    })
}

try {
    Invoke-Gate 'BACKEND JAVASCRIPT SYNTAX' {
        Push-Location (Join-Path $root 'backend')
        try {
            $files = Get-ChildItem .\src, .\tests -Recurse -Filter *.js

            foreach ($file in $files) {
                & node --check $file.FullName
                if ($LASTEXITCODE -ne 0) {
                    throw "Syntax failure: $($file.FullName)"
                }
            }
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'BACKEND UNIT AND API TESTS' {
        Push-Location (Join-Path $root 'backend')
        try {
            & npm test
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'FRONTEND TESTS' {
        Push-Location (Join-Path $root 'frontend')
        try {
            & npm test
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'FRONTEND LINT' {
        Push-Location (Join-Path $root 'frontend')
        try {
            & npm run lint
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'BACKEND LINT' {
        Push-Location (Join-Path $root 'frontend')
        try {
            & .\node_modules\.bin\eslint.cmd --config .\.eslintrc.cjs --no-ignore ..\backend\src ..\backend\tests --max-warnings 0
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'FRONTEND PRODUCTION BUILD' {
        Push-Location (Join-Path $root 'frontend')
        try {
            & npm run build
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'BACKEND DEPENDENCY AUDIT' {
        Push-Location (Join-Path $root 'backend')
        try {
            & npm audit --audit-level=high
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'FRONTEND DEPENDENCY AUDIT' {
        Push-Location (Join-Path $root 'frontend')
        try {
            & npm audit --audit-level=high
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'SEMGREP SAST' {
        Push-Location $root
        try {
            & semgrep scan --config p/javascript --error --no-git-ignore .\backend\src .\frontend\src
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Gate 'OPENAPI CONTRACT VALIDATION' {
        Push-Location $root
        try {
            & npx --yes @redocly/cli lint .\specs\001-smart-todo-manager\contracts\task-api.yaml
        }
        finally {
            Pop-Location
        }
    }
}
finally {
    Write-Host "`n========== HARNESS SUMMARY ==========" -ForegroundColor Cyan
    $script:results | Format-Table -AutoSize

    $failed = @($script:results | Where-Object { $_.Status -eq 'FAIL' }).Count
    $passed = @($script:results | Where-Object { $_.Status -eq 'PASS' }).Count

    Write-Host "Passed gates: $passed"
    Write-Host "Failed gates: $failed"
    Write-Host "Harness transcript: $logPath"

    Stop-Transcript | Out-Null
}

if ($failed -gt 0) {
    exit 1
}

exit 0
