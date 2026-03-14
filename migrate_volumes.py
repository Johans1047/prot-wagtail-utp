#!/usr/bin/env python3
"""
migrate_volumes.py — Migración de volúmenes Docker entre máquinas
Proyecto: JICWeb (Wagtail + PostgreSQL + MinIO)

USO:
  python migrate_volumes.py list
  python migrate_volumes.py export [--dir ./backups]
  python migrate_volumes.py transfer --host USER@IP [--dir ./backups]
  python migrate_volumes.py import [--dir ./backups]

# Ver estado de los 3 volúmenes
python migrate_volumes.py list

# PC origen — exportar
python migrate_volumes.py export --dir ./backups

# PC origen — enviar al destino
python migrate_volumes.py transfer --host ubuntu@192.168.1.100 --dir ./backups

# PC destino — importar
python migrate_volumes.py import --dir /tmp/jicweb_volumes
"""

import argparse
import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ─── Configuración ────────────────────────────────────────────────────────────

VOLUMES = [
    "prototipo-utp_jicweb_master_data_v1",        # PostgreSQL master
    "prototipo-utp_jicst_storage_data",           # MinIO storage
    "prototipo-utp_static_files",                 # Wagtail static files
    "prototipo-utp_jicweb_master_data_backup_v1", # PostgreSQL backup
    "prototipo-utp_jicst_backup_data",            # MinIO backup
]

COMPOSE_FILE = "docker-compose.yml"
DEFAULT_BACKUP_DIR = Path("./volume_backups")
REMOTE_TMP_DIR = "/tmp/jicweb_volumes"

# ─── Colores ANSI ─────────────────────────────────────────────────────────────

class C:
    GREEN  = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED    = "\033[0;31m"
    CYAN   = "\033[0;36m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def log(msg):   print(f"{C.GREEN}[✓]{C.RESET} {msg}")
def warn(msg):  print(f"{C.YELLOW}[!]{C.RESET} {msg}")
def error(msg): print(f"{C.RED}[✗]{C.RESET} {msg}", file=sys.stderr); sys.exit(1)
def header(msg):
    bar = "═" * (len(msg) + 8)
    print(f"\n{C.BOLD}{C.CYAN}{bar}")
    print(f"    {msg}")
    print(f"{bar}{C.RESET}")
def hr(): print(f"{C.CYAN}{'─' * 44}{C.RESET}")

def bytes_to_human(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

# ─── Helpers Docker ───────────────────────────────────────────────────────────

def run(cmd: list[str], check=True, capture=False) -> subprocess.CompletedProcess:
    """Ejecuta un comando. Si falla imprime el error y termina (si check=True)."""
    result = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        error(f"Falló: {' '.join(cmd)}\n  {stderr}")
    return result

def check_docker():
    if run(["docker", "info"], check=False, capture=True).returncode != 0:
        error("Docker no está disponible o no está corriendo.")

def volume_exists(name: str) -> bool:
    result = run(["docker", "volume", "ls", "--format", "{{.Name}}"], capture=True)
    return name in result.stdout.splitlines()

def stop_compose():
    if Path(COMPOSE_FILE).exists():
        warn("Deteniendo contenedores para garantizar consistencia de datos...")
        run(["docker", "compose", "-f", COMPOSE_FILE, "stop"], check=False)
    else:
        warn(f"No se encontró {COMPOSE_FILE} — asegúrate de detener los contenedores manualmente.")

def start_compose():
    if Path(COMPOSE_FILE).exists():
        print(f"\n{C.YELLOW}Para levantar los servicios:{C.RESET}")
        print(f"  {C.CYAN}docker compose -f {COMPOSE_FILE} up -d{C.RESET}\n")

def get_volume_size(name: str) -> str:
    """Retorna el tamaño del mountpoint de un volumen."""
    result = run(
        ["docker", "volume", "inspect", name, "--format", "{{.Mountpoint}}"],
        capture=True, check=False,
    )
    mountpoint = result.stdout.strip()
    if not mountpoint:
        return "n/a"
    
    # En Windows, usar PowerShell; en Linux/Mac usar du
    if sys.platform == "win32":
        ps_cmd = (
            f"(Get-ChildItem -Path '{mountpoint}' -Recurse -Force | "
            f"Measure-Object -Property Length -Sum).Sum"
        )
        r = run(["powershell", "-Command", ps_cmd], capture=True, check=False)
    else:
        r = run(["du", "-sh", mountpoint], capture=True, check=False)
    
    if r.returncode == 0:
        try:
            if sys.platform == "win32":
                size_bytes = int(r.stdout.strip())
                return bytes_to_human(size_bytes)
            else:
                return r.stdout.split()[0]
        except (ValueError, IndexError):
            return "n/a"
    return "n/a"

# ─── EXPORT ───────────────────────────────────────────────────────────────────

def cmd_export(backup_dir: Path):
    header("EXPORTANDO VOLÚMENES")
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    stop_compose()

    exported = []
    for vol in VOLUMES:
        hr()
        print(f"  Volumen: {C.BOLD}{vol}{C.RESET}")

        if not volume_exists(vol):
            warn(f"  El volumen '{vol}' no existe — saltando.")
            continue

        out_name = f"{vol}__{timestamp}.tar.gz"
        out_path = backup_dir / out_name
        abs_backup = str(backup_dir.resolve())

        print("  Exportando...", end="", flush=True)
        run([
            "docker", "run", "--rm",
            "-v", f"{vol}:/data:ro",
            "-v", f"{abs_backup}:/backup",
            "alpine",
            "sh", "-c", f"tar czf /backup/{out_name} -C /data . 2>/dev/null",
        ])

        size = out_path.stat().st_size if out_path.exists() else 0
        log(f"  → {out_path}  ({bytes_to_human(size)})")
        exported.append(out_path)

    hr()
    log(f"Exportación completada en: {backup_dir.resolve()}")
    print(f"\n{C.YELLOW}Próximo paso — transferir al destino:{C.RESET}")
    print(f"  {C.CYAN}python migrate_volumes.py transfer --host USER@IP --dir {backup_dir}{C.RESET}")

# ─── IMPORT ───────────────────────────────────────────────────────────────────

def cmd_import(backup_dir: Path):
    header("IMPORTANDO VOLÚMENES")

    tar_files = sorted(backup_dir.glob("*.tar.gz"))
    if not tar_files:
        error(f"No se encontraron archivos .tar.gz en: {backup_dir}")

    # Agrupar por nombre de volumen, tomar el más reciente de cada uno
    latest: dict[str, Path] = {}
    for f in tar_files:
        # Formato: VOLUME_NAME__TIMESTAMP.tar.gz
        match = re.match(r"^(.+)__(\d{8}_\d{6})\.tar\.gz$", f.name)
        if not match:
            warn(f"  Archivo con nombre inesperado, saltando: {f.name}")
            continue
        vol_name, ts = match.group(1), match.group(2)
        if vol_name not in latest or ts > re.search(r"__(\d+_\d+)\.tar\.gz$", latest[vol_name].name).group(1):
            latest[vol_name] = f

    stop_compose()

    for vol in VOLUMES:
        hr()
        print(f"  Volumen: {C.BOLD}{vol}{C.RESET}")

        if vol not in latest:
            warn(f"  No se encontró backup para '{vol}' — saltando.")
            continue

        tarfile = latest[vol]
        print(f"  Archivo: {tarfile.name}")

        if not volume_exists(vol):
            run(["docker", "volume", "create", vol], capture=True)
            log(f"  Volumen '{vol}' creado.")
        else:
            warn(f"  El volumen '{vol}' ya existe — se sobreescribirá su contenido.")

        abs_dir = str(tarfile.parent.resolve())
        print("  Importando...", end="", flush=True)
        run([
            "docker", "run", "--rm",
            "-v", f"{vol}:/data",
            "-v", f"{abs_dir}:/backup:ro",
            "alpine",
            "sh", "-c",
            f"rm -rf /data/* /data/..?* /data/.[!.]* 2>/dev/null; "
            f"tar xzf /backup/{tarfile.name} -C /data",
        ])
        log("  Importado correctamente.")

    hr()
    log("Importación completada.")
    start_compose()

# ─── TRANSFER ─────────────────────────────────────────────────────────────────

def cmd_transfer(remote_host: str, backup_dir: Path):
    header(f"TRANSFIRIENDO A {remote_host}")

    tar_files = sorted(backup_dir.glob("*.tar.gz"))
    if not tar_files:
        error(f"No hay archivos .tar.gz en {backup_dir}. Ejecuta primero: export")

    log(f"Creando directorio remoto {REMOTE_TMP_DIR} en {remote_host}...")
    run(["ssh", remote_host, f"mkdir -p {REMOTE_TMP_DIR}"])

    for f in tar_files:
        print(f"  Enviando {f.name}...", end="", flush=True)
        run(["scp", "-C", str(f), f"{remote_host}:{REMOTE_TMP_DIR}/"])
        log("  OK")

    hr()
    log("Transferencia completada.")
    print(f"\n{C.YELLOW}Próximo paso — en {remote_host}:{C.RESET}")
    print(f"  {C.CYAN}python migrate_volumes.py import --dir {REMOTE_TMP_DIR}{C.RESET}\n")

# ─── LIST ─────────────────────────────────────────────────────────────────────

def cmd_list():
    header("VOLÚMENES DOCKER DEL PROYECTO")
    print(f"  {'NOMBRE':<35} {'ESTADO':<12} TAMAÑO")
    hr()
    for vol in VOLUMES:
        if volume_exists(vol):
            size = get_volume_size(vol)
            print(f"  {C.GREEN}{vol:<35}{C.RESET} {'existe':<12} {size}")
        else:
            print(f"  {C.YELLOW}{vol:<35}{C.RESET} no existe")
    print()

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="migrate_volumes.py",
        description="Migración de volúmenes Docker entre máquinas — JICWeb",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ejemplos:
  python migrate_volumes.py list
  python migrate_volumes.py export --dir ./backups
  python migrate_volumes.py transfer --host ubuntu@192.168.1.100 --dir ./backups
  python migrate_volumes.py import --dir /tmp/jicweb_volumes
        """,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="Muestra el estado actual de los volúmenes")

    # export
    p_export = sub.add_parser("export", help="Exporta los volúmenes a archivos .tar.gz")
    p_export.add_argument("--dir", type=Path, default=DEFAULT_BACKUP_DIR,
                          help=f"Directorio de destino (default: {DEFAULT_BACKUP_DIR})")

    # import
    p_import = sub.add_parser("import", help="Importa los volúmenes desde archivos .tar.gz")
    p_import.add_argument("--dir", type=Path, default=DEFAULT_BACKUP_DIR,
                          help=f"Directorio con los .tar.gz (default: {DEFAULT_BACKUP_DIR})")

    # transfer
    p_transfer = sub.add_parser("transfer", help="Envía los .tar.gz al PC destino vía SCP")
    p_transfer.add_argument("--host", required=True,
                            help="Destino SSH, ej: ubuntu@192.168.1.100")
    p_transfer.add_argument("--dir", type=Path, default=DEFAULT_BACKUP_DIR,
                            help=f"Directorio con los .tar.gz (default: {DEFAULT_BACKUP_DIR})")

    args = parser.parse_args()
    check_docker()

    match args.command:
        case "list":     cmd_list()
        case "export":   cmd_export(args.dir)
        case "import":   cmd_import(args.dir)
        case "transfer": cmd_transfer(args.host, args.dir)

if __name__ == "__main__":
    main()