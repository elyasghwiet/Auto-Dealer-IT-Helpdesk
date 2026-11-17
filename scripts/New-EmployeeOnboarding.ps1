<#
.SYNOPSIS
  Onboards new employees from a CSV file: creates accounts, adds department groups,
  generates a temporary password, and writes a report. Safe to run with -WhatIf.

.DESCRIPTION
  Modes:
    Simulation (default) - no real accounts are created; everything is written to the output files.
    Local                - creates real LOCAL Windows accounts (needs an elevated PowerShell).
  In a company with Active Directory, replace the 'Create-Account' function with New-ADUser.

.PARAMETER CsvPath   CSV with columns FirstName,LastName,Department,JobTitle,Manager
.PARAMETER Mode      Simulation or Local
.PARAMETER OutDir    Folder for the report and credentials file (default .\output)

.EXAMPLE
  .\New-EmployeeOnboarding.ps1 -CsvPath ..\data\new_hires.csv -WhatIf
.EXAMPLE
  .\New-EmployeeOnboarding.ps1 -CsvPath ..\data\new_hires.csv -Mode Simulation
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)][string]$CsvPath,
    [ValidateSet('Simulation', 'Local')][string]$Mode = 'Simulation',
    [string]$OutDir = '.\output'
)

$ErrorActionPreference = 'Stop'
$ManualMinutesPerUser = 12     # estimate of the manual process: account 3, groups 2, mailbox 3, password 2, ticket 2

$GroupMap = @{
    'IT'         = @('it-staff', 'remote-access')
    'HR'         = @('hr-users', 'payroll-readonly')
    'Finance'    = @('finance-users', 'erp-access')
    'Sales'      = @('sales-users', 'crm-access')
    'Operations' = @('ops-users', 'fleet-dashboard')
}
$DefaultGroups = @('all-staff')

function New-TempPassword {
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*'
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    do {
        $bytes = New-Object byte[] 14
        $rng.GetBytes($bytes)
        $pw = -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })
    } until ($pw -cmatch '[a-z]' -and $pw -cmatch '[A-Z]' -and $pw -match '\d' -and $pw -match '[!@#$%&*]')
    return $pw
}

function ConvertTo-Username([string]$First, [string]$Last, [System.Collections.Generic.HashSet[string]]$Taken) {
    $clean = { param($s) ($s.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}', '' -replace '[^a-zA-Z]', '').ToLower() }
    $f = & $clean $First; $l = & $clean $Last
    if (-not $f -or -not $l) { throw "Name '$First $Last' has no usable letters for a username" }
    $base = ($f.Substring(0, 1) + $l)
    if ($base.Length -gt 20) { $base = $base.Substring(0, 20) }
    $name = $base; $n = 2
    while ($Taken.Contains($name)) { $name = "$base$n"; $n++ }
    return $name
}

function Create-Account([string]$User, [string]$Full, [string]$Title, [string]$Password, [string[]]$Groups) {
    if ($Mode -eq 'Simulation') { return }
    $secure = ConvertTo-SecureString $Password -AsPlainText -Force
    New-LocalUser -Name $User -FullName $Full -Description $Title -Password $secure -PasswordNeverExpires:$false | Out-Null
    foreach ($g in $Groups) {
        if (-not (Get-LocalGroup -Name $g -ErrorAction SilentlyContinue)) { New-LocalGroup -Name $g | Out-Null }
        Add-LocalGroupMember -Group $g -Member $User
    }
}

# ---------------------------------------------------------------- main
$sw = [System.Diagnostics.Stopwatch]::StartNew()
if (-not (Test-Path -LiteralPath $CsvPath)) { Write-Error "CSV file not found: $CsvPath"; exit 2 }
$rows = @(Import-Csv -LiteralPath $CsvPath -Encoding UTF8)
$required = 'FirstName', 'LastName', 'Department', 'JobTitle', 'Manager'
foreach ($c in $required) {
    if ($rows.Count -gt 0 -and -not ($rows[0].PSObject.Properties.Name -contains $c)) {
        Write-Error "CSV is missing required column: $c"; exit 2
    }
}
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$taken = New-Object 'System.Collections.Generic.HashSet[string]'
if ($Mode -eq 'Local') { Get-LocalUser | ForEach-Object { [void]$taken.Add($_.Name.ToLower()) } }

$results = New-Object System.Collections.ArrayList
$creds = New-Object System.Collections.ArrayList
$line = 1
foreach ($r in $rows) {
    $line++
    $full = "$($r.FirstName) $($r.LastName)".Trim()
    try {
        if (-not $GroupMap.ContainsKey($r.Department)) { throw "Unknown department '$($r.Department)'" }
        $user = ConvertTo-Username $r.FirstName $r.LastName $taken
        $groups = @($DefaultGroups + $GroupMap[$r.Department])
        $pw = New-TempPassword
        if ($PSCmdlet.ShouldProcess("$user ($full)", "Create account in groups: $($groups -join ', ')")) {
            Create-Account $user $full $r.JobTitle $pw $groups
            [void]$taken.Add($user)
            [void]$creds.Add([pscustomobject]@{ Username = $user; TemporaryPassword = $pw })
            [void]$results.Add([pscustomobject]@{ Line = $line; Employee = $full; Username = $user; Department = $r.Department; Groups = ($groups -join ';'); Status = 'CREATED'; Detail = "Mode=$Mode" })
        } else {
            [void]$results.Add([pscustomobject]@{ Line = $line; Employee = $full; Username = $user; Department = $r.Department; Groups = ($groups -join ';'); Status = 'WHATIF'; Detail = 'No change made' })
        }
    } catch {
        [void]$results.Add([pscustomobject]@{ Line = $line; Employee = $full; Username = ''; Department = $r.Department; Groups = ''; Status = 'REJECTED'; Detail = $_.Exception.Message })
    }
}
$sw.Stop()

$stamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$results | Export-Csv -LiteralPath (Join-Path $OutDir "onboarding_report_$stamp.csv") -NoTypeInformation -Encoding UTF8
if ($creds.Count -gt 0 -and -not $WhatIfPreference) {
    $credPath = Join-Path $OutDir "temporary_passwords_$stamp.csv"
    $creds | Export-Csv -LiteralPath $credPath -NoTypeInformation -Encoding UTF8
    Write-Warning "Temporary passwords were written to $credPath - hand them over securely, then delete the file."
}

$ok = @($results | Where-Object { $_.Status -in 'CREATED', 'WHATIF' }).Count
$bad = @($results | Where-Object { $_.Status -eq 'REJECTED' }).Count
$manualMin = $ok * $ManualMinutesPerUser
$autoSec = [math]::Round($sw.Elapsed.TotalSeconds, 1)
$results | Format-Table Line, Employee, Username, Department, Status, Detail -AutoSize
Write-Host ("Processed {0} row(s): {1} ok, {2} rejected." -f $rows.Count, $ok, $bad)
Write-Host ("Time: script {0} s vs about {1} min by hand ({2} min per user, estimate) = {3} min saved." -f $autoSec, $manualMin, $ManualMinutesPerUser, ($manualMin - [math]::Round($autoSec / 60, 1)))
if ($bad -gt 0) { exit 1 } else { exit 0 }
