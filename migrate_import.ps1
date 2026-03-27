[CmdletBinding()]
param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$BackupSource,
    [switch]$SkipStart,
    [switch]$SkipEnvRestore
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

function Find-LatestBackupSource {
    $cwd = (Get-Location).Path

    $zip = Get-ChildItem -LiteralPath $cwd -Filter "migration_backup_*.zip" -File |
        Sort-Object -Property LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -ne $zip) {
        return $zip.FullName
    }

    $dir = Get-ChildItem -LiteralPath $cwd -Directory |
        Where-Object { $_.Name -like "migration_backup_*" } |
        Sort-Object -Property LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -ne $dir) {
        return $dir.FullName
    }

    return $null
}

function Ensure-DockerVolume {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VolumeName
    )

    if (-not (Test-DockerVolumeExists -VolumeName $VolumeName)) {
        Write-Host "Creando volumen $VolumeName"
        Run-Checked -Command "docker" -Arguments @("volume", "create", $VolumeName) -ErrorMessage "No se pudo crear el volumen $VolumeName"
    }
}

function Restore-DockerVolume {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectName,
        [Parameter(Mandatory = $true)]
        [string]$VolumeSuffix,
        [Parameter(Mandatory = $true)]
        [string]$BackupDir
    )

    $archiveName = "$VolumeSuffix.tar.gz"
    $archivePath = Join-Path $BackupDir $archiveName
    if (-not (Test-Path -LiteralPath $archivePath)) {
        throw "No se encontro el archivo de backup requerido: $archivePath"
    }

    $targetVolume = "${ProjectName}_${VolumeSuffix}"
    Ensure-DockerVolume -VolumeName $targetVolume

    Write-Host "Limpiando volumen $targetVolume"
    Run-Checked -Command "docker" -Arguments @(
        "run", "--rm",
        "-v", "${targetVolume}:/to",
        "alpine", "sh", "-c",
        "find /to -mindepth 1 -maxdepth 1 -exec rm -rf {} +"
    ) -ErrorMessage "No se pudo limpiar el volumen $targetVolume"

    Write-Host "Restaurando $archiveName -> $targetVolume"
    Run-Checked -Command "docker" -Arguments @(
        "run", "--rm",
        "-v", "${targetVolume}:/to",
        "-v", "${BackupDir}:/backup:ro",
        "alpine", "sh", "-c",
        "cd /to && tar xzf /backup/$archiveName"
    ) -ErrorMessage "No se pudo restaurar $archiveName en $targetVolume"

    return $targetVolume
}

if (-not (Test-Path -LiteralPath $ComposeFile)) {
    throw "No se encontro el archivo compose: $ComposeFile"
}

if ([string]::IsNullOrWhiteSpace($BackupSource)) {
    $BackupSource = Find-LatestBackupSource
    if ($null -eq $BackupSource) {
        throw "No se encontro BackupSource automaticamente. Pasa -BackupSource con ZIP o carpeta."
    }
}

$projectName = Split-Path -Leaf (Get-Location).Path
Write-Host "Proyecto destino detectado: $projectName"
Write-Host "Fuente de backup: $BackupSource"

$resolvedBackupSource = (Resolve-Path -LiteralPath $BackupSource).Path
$backupDir = $resolvedBackupSource
$extractedTempDir = $null

if ((Get-Item -LiteralPath $resolvedBackupSource).PSIsContainer -eq $false) {
    if ([System.IO.Path]::GetExtension($resolvedBackupSource).ToLowerInvariant() -ne ".zip") {
        throw "BackupSource debe ser una carpeta o un .zip"
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $extractedTempDir = Join-Path (Get-Location).Path "migration_import_$timestamp"
    New-Item -ItemType Directory -Path $extractedTempDir -Force | Out-Null

    Write-Host "Extrayendo backup ZIP..."
    Expand-Archive -LiteralPath $resolvedBackupSource -DestinationPath $extractedTempDir -Force
    $backupDir = $extractedTempDir
}

$requiredVolumeSuffixes = @(
    "jicweb_master_data_v1",
    "jicst_storage_data"
)

$optionalVolumeSuffixes = @(
    "jicweb_master_data_backup_v1",
    "jicst_backup_data"
)

$availableArchives = Get-ChildItem -LiteralPath $backupDir -Filter "*.tar.gz" -File | Select-Object -ExpandProperty Name

foreach ($suffix in $requiredVolumeSuffixes) {
    if ($availableArchives -notcontains "$suffix.tar.gz") {
        throw "Falta backup requerido en ${backupDir}: $suffix.tar.gz"
    }
}

if (-not $SkipEnvRestore) {
    foreach ($envName in @(".env.prod", ".env")) {
        $src = Join-Path $backupDir $envName
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path (Get-Location).Path $envName) -Force
            Write-Host "Restaurado $envName"
        }
    }
}

Write-Host "Deteniendo stack actual para restaurar datos..."
Run-Checked -Command "docker" -Arguments @("compose", "-p", $projectName, "-f", $ComposeFile, "down") -ErrorMessage "No se pudo detener el stack"

$restoredVolumes = @()
foreach ($suffix in $requiredVolumeSuffixes) {
    $restoredVolumes += Restore-DockerVolume -ProjectName $projectName -VolumeSuffix $suffix -BackupDir $backupDir
}

foreach ($suffix in $optionalVolumeSuffixes) {
    if ($availableArchives -contains "$suffix.tar.gz") {
        $restoredVolumes += Restore-DockerVolume -ProjectName $projectName -VolumeSuffix $suffix -BackupDir $backupDir
    }
}

if (-not $SkipStart) {
    Write-Host "Levantando stack con build..."
    Run-Checked -Command "docker" -Arguments @("compose", "-p", $projectName, "-f", $ComposeFile, "up", "-d", "--build") -ErrorMessage "No se pudo iniciar el stack"
}

Write-Host ""
Write-Host "Importacion completada."
Write-Host "Volumenes restaurados:"
$restoredVolumes | ForEach-Object { Write-Host " - $_" }

if ($null -ne $extractedTempDir) {
    Write-Host ""
    Write-Host "Se uso carpeta temporal: $extractedTempDir"
    Write-Host "Puedes eliminarla cuando confirmes que todo funciona."
}
