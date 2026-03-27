[CmdletBinding()]
param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$OutputDir,
    [switch]$IncludeOptional
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Run-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$ErrorMessage (exit code $LASTEXITCODE)."
    }
}

function Test-DockerVolumeExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VolumeName
    )

    & docker volume inspect $VolumeName *> $null
    return $LASTEXITCODE -eq 0
}

function Export-DockerVolume {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectName,
        [Parameter(Mandatory = $true)]
        [string]$VolumeSuffix,
        [Parameter(Mandatory = $true)]
        [string]$DestinationDir
    )

    $sourceVolume = "${ProjectName}_${VolumeSuffix}"
    if (-not (Test-DockerVolumeExists -VolumeName $sourceVolume)) {
        throw "No existe el volumen requerido: $sourceVolume"
    }

    $archiveName = "$VolumeSuffix.tar.gz"
    Write-Host "Exportando $sourceVolume -> $archiveName"

    Run-Checked -Command "docker" -Arguments @(
        "run", "--rm",
        "-v", "${sourceVolume}:/from:ro",
        "-v", "${DestinationDir}:/backup",
        "alpine", "sh", "-c",
        "cd /from && tar czf /backup/$archiveName ."
    ) -ErrorMessage "Fallo la exportacion del volumen $sourceVolume"

    return [PSCustomObject]@{
        suffix       = $VolumeSuffix
        sourceVolume = $sourceVolume
        archive      = $archiveName
    }
}

if (-not (Test-Path -LiteralPath $ComposeFile)) {
    throw "No se encontro el archivo compose: $ComposeFile"
}

$projectName = Split-Path -Leaf (Get-Location).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path (Get-Location).Path "migration_backup_$timestamp"
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$requiredVolumeSuffixes = @(
    "jicweb_master_data_v1",
    "jicst_storage_data"
)

$optionalVolumeSuffixes = @(
    "jicweb_master_data_backup_v1",
    "jicst_backup_data"
)

Write-Host "Proyecto detectado: $projectName"
Write-Host "Deteniendo stack para congelar datos..."
Run-Checked -Command "docker" -Arguments @("compose", "-p", $projectName, "-f", $ComposeFile, "down") -ErrorMessage "No se pudo detener el stack"

$exported = @()

foreach ($suffix in $requiredVolumeSuffixes) {
    $exported += Export-DockerVolume -ProjectName $projectName -VolumeSuffix $suffix -DestinationDir $OutputDir
}

if ($IncludeOptional) {
    foreach ($suffix in $optionalVolumeSuffixes) {
        $volumeName = "${projectName}_${suffix}"
        if (Test-DockerVolumeExists -VolumeName $volumeName) {
            $exported += Export-DockerVolume -ProjectName $projectName -VolumeSuffix $suffix -DestinationDir $OutputDir
        }
        else {
            Write-Warning "Se omite volumen opcional no encontrado: $volumeName"
        }
    }
}

$envCandidates = @(".env.prod", ".env")
foreach ($envFile in $envCandidates) {
    if (Test-Path -LiteralPath $envFile) {
        Copy-Item -LiteralPath $envFile -Destination (Join-Path $OutputDir (Split-Path -Leaf $envFile)) -Force
    }
}

$metadata = [PSCustomObject]@{
    exportedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    sourceProject = $projectName
    composeFile   = $ComposeFile
    includeOptional = [bool]$IncludeOptional
    volumes       = $exported
}

$metadata | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDir "metadata.json") -Encoding UTF8

$archives = Get-ChildItem -LiteralPath $OutputDir -Filter "*.tar.gz" -File
if ($archives.Count -gt 0) {
    $hashLines = $archives |
        Sort-Object -Property Name |
        ForEach-Object {
            $hash = Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
            "{0}  {1}" -f $hash.Hash, $_.Name
        }

    Set-Content -LiteralPath (Join-Path $OutputDir "SHA256SUMS.txt") -Value $hashLines -Encoding UTF8
}

$zipPath = "$OutputDir.zip"
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $OutputDir "*") -DestinationPath $zipPath -Force

Write-Host ""
Write-Host "Exportacion completada."
Write-Host "Carpeta: $OutputDir"
Write-Host "ZIP: $zipPath"
Write-Host ""
Write-Host "En la PC destino ejecuta migrate_import.ps1 desde la carpeta del proyecto destino."
