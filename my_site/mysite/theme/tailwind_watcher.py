import subprocess
from pathlib import Path
import os
import shutil

def run_tailwind_watch():
    """
    Runs TailwindCSS in watch mode for automatic recompilation.
    """
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent
    input_css = project_root / 'theme' / 'static' / 'src' / 'input.css'
    output_css = project_root / 'theme' / 'static' / 'src' / 'output.css'
    
    # Buscar Git Bash
    git_bash_locations = [
        r'C:\Program Files\Git\bin\bash.exe',
        r'C:\Program Files (x86)\Git\bin\bash.exe',
        shutil.which('bash')
    ]
    
    git_bash = None
    for location in git_bash_locations:
        if location and os.path.exists(location):
            git_bash = location
            break
    
    if not git_bash:
        print("\n" + "="*60)
        print("❌ ERROR: Git Bash no encontrado")
        print("="*60)
        print("Por favor instala Git Bash o usa npx directamente.")
        print("="*60 + "\n")
        return
    
    # Comando para ejecutar Tailwind
    tailwind_command = f'npx @tailwindcss/cli -i "{input_css}" -o "{output_css}" --watch'
    command = [git_bash, '-c', tailwind_command]
    
    # Impresiones legibles
    print("\n" + "="*60)
    print("🎨 INICIANDO TAILWIND CSS WATCHER")
    print("="*60)
    print(f"📂 Directorio del proyecto: {project_root}")
    print(f"🔧 Git Bash: {git_bash}")
    print(f"📥 Input CSS: {input_css}")
    print(f"📤 Output CSS: {output_css}")
    print("="*60)
    print("⚡ Ejecutando comando...")
    print(f"   {tailwind_command}")
    print("="*60 + "\n")
    
    try:
        subprocess.Popen(command, cwd=str(project_root))
        print("✅ TailwindCSS watcher iniciado correctamente")
        print("🔄 Observando cambios en tus archivos CSS...\n")
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ ERROR al iniciar TailwindCSS")
        print("="*60)
        print(f"Detalles: {e}")
        print("="*60 + "\n")
