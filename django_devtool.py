#!/usr/bin/env python3
"""
Django/Wagtail DevTool - Automated project setup with TailwindCSS
Author: DevTool Generator
Version: 1.0.0
"""

import argparse
import subprocess
import sys
import platform
import os
import shutil
from pathlib import Path
from typing import Optional, List


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DevTool:
    """Main DevTool class for Django/Wagtail project setup"""
    
    def __init__(self, project_name: str, framework: str = "wagtail", venv_name: str = "venv"):
        self.project_name = project_name
        self.framework = framework
        self.venv_name = venv_name
        self.project_root = Path.cwd() / project_name
        self.venv_path = self.project_root / venv_name
        
    def print_header(self, message: str):
        """Print a formatted header message"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print an info message"""
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, shell: bool = False) -> bool:
        """Execute a shell command and return success status"""
        try:
            # On Windows, use shell=True for npm/npx commands to work with nvm
            if platform.system() == "Windows" and command[0] in ["npm", "npx", "node"]:
                shell = True
            
            if shell:
                result = subprocess.run(" ".join(command), shell=True, cwd=cwd, check=True)
            else:
                result = subprocess.run(command, cwd=cwd, check=True)
            return result.returncode == 0
        except FileNotFoundError as e:
            self.print_error(f"Command not found: {command[0]}")
            self.print_error(f"Please make sure {command[0]} is installed and in your PATH")
            if command[0] in ["npm", "npx"] and sys.platform == "win32":
                self.print_warning("If you're using nvm, make sure it's properly configured")
                self.print_info("Try running this in a regular CMD or PowerShell window")
            return False
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {' '.join(command)}")
            self.print_error(f"Error: {e}")
            return False
    
    def create_project_structure(self):
        """Create the main project directory"""
        self.print_header("📁 Creating Project Structure")
        
        if self.project_root.exists():
            self.print_error(f"Project directory '{self.project_name}' already exists!")
            return False
        
        self.project_root.mkdir(parents=True)
        self.print_success(f"Created project directory: {self.project_root}")
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        self.print_header("🐍 Creating Virtual Environment")
        
        if self.run_command([sys.executable, "-m", "venv", str(self.venv_path)]):
            self.print_success(f"Virtual environment created: {self.venv_name}")
            return True
        return False
    
    def get_pip_path(self) -> Path:
        """Get the pip executable path for the virtual environment"""
        if sys.platform == "win32":
            return self.venv_path / "Scripts" / "pip.exe"
        return self.venv_path / "bin" / "pip"
    
    def get_python_path(self) -> Path:
        """Get the python executable path for the virtual environment"""
        if sys.platform == "win32":
            return self.venv_path / "Scripts" / "python.exe"
        return self.venv_path / "bin" / "python"
    
    def install_python_dependencies(self):
        """Install required Python packages"""
        self.print_header("📦 Installing Python Dependencies")
        
        pip_path = self.get_pip_path()
        
        packages = ["django-livereload-server"]
        if self.framework == "wagtail":
            packages.insert(0, "wagtail")
        else:
            packages.insert(0, "django")
        
        for package in packages:
            self.print_info(f"Installing {package}...")
            if not self.run_command([str(pip_path), "install", package]):
                return False
            self.print_success(f"Installed {package}")
        
        return True
    
    def initialize_npm(self):
        """Initialize npm and install TailwindCSS"""
        self.print_header("📦 Initializing NPM and TailwindCSS")
        
        # Create package.json
        package_json = {
            "name": self.project_name,
            "version": "1.0.0",
            "main": "index.js",
            "scripts": {
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "keywords": [],
            "author": "",
            "license": "ISC",
            "description": ""
        }
        
        if not self.run_command(["npm", "init", "-y"], cwd=self.project_root):
            return False
        self.print_success("Initialized package.json")
        
        # Install TailwindCSS
        self.print_info("Installing TailwindCSS...")
        if not self.run_command(["npm", "install", "tailwindcss", "@tailwindcss/cli"], cwd=self.project_root):
            return False
        self.print_success("Installed TailwindCSS")
        
        return True
    
    def create_tailwind_config(self):
        """Create TailwindCSS configuration file"""
        self.print_header("⚙️  Creating TailwindCSS Configuration")
        
        config_content = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {},
      fontFamily: {},
    },
  },
  plugins: [],
}
"""
        
        config_path = self.project_root / "tailwind.config.js"
        config_path.write_text(config_content)
        self.print_success("Created tailwind.config.js")
        return True
    
    def create_django_project(self):
        """Create Django or Wagtail project"""
        self.print_header(f"🚀 Creating {self.framework.capitalize()} Project")
        
        python_path = self.get_python_path()
            
        if self.framework == "wagtail":
            wagtail_cmd = "wagtail.exe" if os.name == "nt" else "wagtail"
            wagtail_path = python_path.parent / wagtail_cmd

            if not self.run_command(
                [str(wagtail_path), "start", "mysite"],
                cwd=self.project_root
            ):
                return False
        else:
            if not self.run_command(
                [str(python_path), "-m", "django", "startproject", "mysite"],
                cwd=self.project_root
            ):
                return False
        
        self.print_success(f"Created {self.framework} project: mysite")
        
        # Run migrations
        mysite_path = self.project_root / "mysite"
        manage_py = mysite_path / "manage.py"
        
        self.print_info("Running migrations...")
        if not self.run_command([str(python_path), str(manage_py), "migrate"], cwd=mysite_path):
            return False
        self.print_success("Migrations completed")
        
        return True
    
    def create_theme_app(self):
        """Create theme app with TailwindCSS setup"""
        self.print_header("🎨 Creating Theme App")
        
        mysite_path = self.project_root / "mysite"
        python_path = self.get_python_path()
        manage_py = mysite_path / "manage.py"
        
        # Create theme app
        if not self.run_command([str(python_path), str(manage_py), "startapp", "theme"], cwd=mysite_path):
            return False
        self.print_success("Created theme app")
        
        theme_path = mysite_path / "theme"
        
        # Remove unnecessary files
        files_to_remove = ["admin.py", "models.py", "tests.py", "views.py"]
        for file in files_to_remove:
            file_path = theme_path / file
            if file_path.exists():
                file_path.unlink()
        self.print_success("Cleaned up theme app")
        
        # Create static/src directory
        static_src = theme_path / "static" / "src"
        static_src.mkdir(parents=True, exist_ok=True)
        
        # Create input.css
        input_css = static_src / "input.css"
        input_css.write_text("@import \"tailwindcss\";\n")
        self.print_success("Created input.css")
        
        # Create tailwind_watcher.py
        self.create_tailwind_watcher(theme_path)
        
        return True
    
    def create_tailwind_watcher(self, theme_path: Path):
        """Create the TailwindCSS watcher script"""
        watcher_content = """import subprocess
from pathlib import Path
import os
import shutil

def run_tailwind_watch():
    \"\"\"
    Runs TailwindCSS in watch mode for automatic recompilation.
    \"\"\"
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent
    input_css = project_root / 'theme' / 'static' / 'src' / 'input.css'
    output_css = project_root / 'theme' / 'static' / 'src' / 'output.css'
    
    # Buscar Git Bash
    git_bash_locations = [
        r'C:\\Program Files\\Git\\bin\\bash.exe',
        r'C:\\Program Files (x86)\\Git\\bin\\bash.exe',
        shutil.which('bash')
    ]
    
    git_bash = None
    for location in git_bash_locations:
        if location and os.path.exists(location):
            git_bash = location
            break
    
    if not git_bash:
        print("\\n" + "="*60)
        print("❌ ERROR: Git Bash no encontrado")
        print("="*60)
        print("Por favor instala Git Bash o usa npx directamente.")
        print("="*60 + "\\n")
        return
    
    # Comando para ejecutar Tailwind
    tailwind_command = f'npx @tailwindcss/cli -i "{input_css}" -o "{output_css}" --watch'
    command = [git_bash, '-c', tailwind_command]
    
    # Impresiones legibles
    print("\\n" + "="*60)
    print("🎨 INICIANDO TAILWIND CSS WATCHER")
    print("="*60)
    print(f"📂 Directorio del proyecto: {project_root}")
    print(f"🔧 Git Bash: {git_bash}")
    print(f"📥 Input CSS: {input_css}")
    print(f"📤 Output CSS: {output_css}")
    print("="*60)
    print("⚡ Ejecutando comando...")
    print(f"   {tailwind_command}")
    print("="*60 + "\\n")
    
    try:
        subprocess.Popen(command, cwd=str(project_root))
        print("✅ TailwindCSS watcher iniciado correctamente")
        print("🔄 Observando cambios en tus archivos CSS...\\n")
    except Exception as e:
        print("\\n" + "="*60)
        print(f"❌ ERROR al iniciar TailwindCSS")
        print("="*60)
        print(f"Detalles: {e}")
        print("="*60 + "\\n")
"""
        
        watcher_path = theme_path / "tailwind_watcher.py"
        watcher_path.write_text(watcher_content, encoding="utf-8")
        self.print_success("Created tailwind_watcher.py")
    
    def create_web_app(self):
        """Create web app with views and templates"""
        self.print_header("🌐 Creating Web App")
        
        mysite_path = self.project_root / "mysite"
        python_path = self.get_python_path()
        manage_py = mysite_path / "manage.py"
        
        # Create web app
        if not self.run_command([str(python_path), str(manage_py), "startapp", "web"], cwd=mysite_path):
            return False
        self.print_success("Created web app")
        
        web_path = mysite_path / "web"
        
        # Remove unnecessary files
        files_to_remove = ["admin.py", "models.py", "tests.py"]
        for file in files_to_remove:
            file_path = web_path / file
            if file_path.exists():
                file_path.unlink()
        self.print_success("Cleaned up web app")
        
        # Create views.py
        views_content = """from django.shortcuts import render

def home(request):
    photo_data = {
        'photo_1': 'https://picsum.photos/seed/1/300/200',
        'photo_2': 'https://picsum.photos/seed/2/300/400',
        'photo_3': 'https://picsum.photos/seed/3/300/300',
        'photo_4': 'https://picsum.photos/seed/4/300/300',
        'photo_5': 'https://picsum.photos/seed/5/300/300',
        'photo_6': 'https://picsum.photos/seed/6/300/300',
        'photo_7': 'https://picsum.photos/seed/7/300/400',
        'photo_8': 'https://picsum.photos/seed/8/300/300',
        'photo_9': 'https://picsum.photos/seed/9/300/200',
        'photo_10': 'https://picsum.photos/seed/10/300/100',
        'photo_11': 'https://picsum.photos/seed/11/300/400',
        'photo_12': 'https://picsum.photos/seed/12/300/400',
    }
    return render(request, 'home.html', photo_data)
"""
        
        views_path = web_path / "views.py"
        views_path.write_text(views_content)
        self.print_success("Created views.py")
        
        # Create templates directory
        templates_path = web_path / "templates"
        templates_path.mkdir(parents=True, exist_ok=True)
        
        # Create home.html
        home_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Photo Grid with Tailwind CSS</title>
    {% load static %}
    <link
      rel="stylesheet"
      href="{% static 'src/output.css' %}"
      type="text/css"
    />
  </head>

  <body class="flex h-screen items-center justify-center">
    <div class="m-auto w-3/5">
      <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
        <div class="grid gap-4">
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow shadow-lg"
              src="https://picsum.photos/seed/1/300/200"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/2/300/400"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/3/300/300"
              alt=""
            />
          </div>
        </div>
        <div class="grid gap-4">
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/4/300/300"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/5/300/300"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/6/300/300"
              alt=""
            />
          </div>
        </div>
        <div class="grid gap-4">
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/7/300/400"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/8/300/300"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/9/300/200"
              alt=""
            />
          </div>
        </div>
        <div class="grid gap-4">
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/10/300/100"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/11/300/400"
              alt=""
            />
          </div>
          <div>
            <img
              class="h-auto max-w-full rounded-lg shadow"
              src="https://picsum.photos/seed/12/300/400"
              alt=""
            />
          </div>
        </div>
      </div>
    </div>
    {% if debug %}
    <script src="http://127.0.0.1:35729/livereload.js"></script>
    {% endif %}
  </body>
</html>
"""
        
        home_path = templates_path / "home.html"
        home_path.write_text(home_html)
        self.print_success("Created home.html template")
        
        return True
    
    def create_urls(self):
        """Configure URLs"""
        self.print_header("🔗 Configuring URLs")
        
        mysite_path = self.project_root / "mysite"
        mysite_urls_path = mysite_path / "mysite" / "urls.py"
        
        mysite_urls_content = mysite_urls_path.read_text()
        
        # Add web urls to urlpatterns in mysite/urls.py
        if "urlpatterns" in mysite_urls_content:
            # Find INSTALLED_APPS and add our apps
            urls_to_add = ["    path('web/', include('web.urls')),"]
            
            # Find the closing bracket of INSTALLED_APPS
            lines = mysite_urls_content.split('\n')
            new_lines = []
            in_urlpatterns = False
            urls_added = False
            
            for line in lines:
                if "urlpatterns" in line:
                    in_urlpatterns = True
                
                if in_urlpatterns and ']' in line and not urls_added:
                    for app in urls_to_add:
                        new_lines.append(app)
                    urls_added = True
                    in_urlpatterns = False
                
                new_lines.append(line)
            
            mysite_urls_content = '\n'.join(new_lines)

        mysite_urls_path.write_text(mysite_urls_content)

        urls_path = mysite_path / "web" / "urls.py"
        
        urls_content = """from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
"""
        urls_path.write_text(urls_content)
        self.print_success("Configured URLs")
        return True
    
    def configure_settings(self):
        """Configure Django settings.py"""
        self.print_header("⚙️  Configuring Settings")
        
        mysite_path = self.project_root / "mysite"
        
        if self.framework == "wagtail":
            settings_path = mysite_path / "mysite" / "settings" / "base.py"
        else:
            settings_path = mysite_path / "mysite" / "settings.py"
        
        if not settings_path.exists():
            self.print_error("settings.py not found!")
            return False
        
        settings_content = settings_path.read_text()
        
        # Add apps to INSTALLED_APPS
        if "INSTALLED_APPS" in settings_content:
            # Find INSTALLED_APPS and add our apps
            apps_to_add = ["    'theme',", "    'web',", "    'livereload',"]
            
            # Find the closing bracket of INSTALLED_APPS
            lines = settings_content.split('\n')
            new_lines = []
            in_installed_apps = False
            apps_added = False
            
            for line in lines:
                if "INSTALLED_APPS" in line:
                    in_installed_apps = True
                
                if in_installed_apps and ']' in line and not apps_added:
                    for app in apps_to_add:
                        new_lines.append(app)
                    apps_added = True
                    in_installed_apps = False
                
                new_lines.append(line)
            
            settings_content = '\n'.join(new_lines)
        
        # Add TailwindCSS watcher import at the top
        import_line = "from theme.tailwind_watcher import run_tailwind_watch\n"
        if import_line not in settings_content:
            # Add after the first import or at the beginning
            lines = settings_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    lines.insert(i + 1, import_line)
                    break
            settings_content = '\n'.join(lines)
            
        # Add DEBUG watcher code
        if self.framework == "wagtail":
            debug_code = """
# Start TailwindCSS watcher in DEBUG mode
DEBUG = True
if DEBUG:
    run_tailwind_watch()
    """
        else:
            debug_code = """
# Start TailwindCSS watcher in DEBUG mode
if DEBUG:
    run_tailwind_watch()
    """
    
        if "run_tailwind_watch()" not in settings_content:
             # Add after the first import or at the beginning
            lines = settings_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# Application'):
                    lines.insert(i - 1, debug_code)
                    break
            settings_content = '\n'.join(lines)
        
        settings_path.write_text(settings_content)
        self.print_success("Updated settings.py with apps and TailwindCSS watcher")
        
        # Create context_processors.py
        self.create_context_processor(mysite_path / "mysite")
        
        # Update TEMPLATES in settings
        self.update_templates_config(settings_path)
        
        return True
    
    def create_context_processor(self, mysite_dir: Path):
        """Create context_processors.py"""
        context_processor_content = """from django.conf import settings

def debug(request):
    return {'debug': settings.DEBUG}
"""
        
        context_path = mysite_dir / "context_processors.py"
        context_path.write_text(context_processor_content)
        self.print_success("Created context_processors.py")
    
    def update_templates_config(self, settings_path: Path):
        """Update TEMPLATES configuration in settings.py"""
        settings_content = settings_path.read_text()
        
        # Add context processor to TEMPLATES
        context_processor_line = "                \"mysite.context_processors.debug\","
        
        if context_processor_line not in settings_content:
            # Find TEMPLATES and add context processor
            settings_content = settings_content.replace(
                '"django.contrib.messages.context_processors.messages",',
                '"django.contrib.messages.context_processors.messages",\n' + context_processor_line
            )
            
            settings_path.write_text(settings_content)
            self.print_success("Updated TEMPLATES with context processor")
    
    def create_startup_script(self):
        """Create a startup script for the project"""
        self.print_header("📝 Creating Startup Scripts")
        
        if sys.platform == "win32":
            # Windows batch file
            startup_content = f"""@echo off
echo Starting Django DevTool Project...
call {self.venv_name}\\Scripts\\activate
cd mysite
python manage.py runserver
"""
            script_path = self.project_root / "start.bat"
        else:
            # Unix shell script
            startup_content = f"""#!/bin/bash
echo "Starting Django DevTool Project..."
source {self.venv_name}/bin/activate
cd mysite
python manage.py runserver
"""
            script_path = self.project_root / "start.sh"
        
        script_path.write_text(startup_content)
        
        if sys.platform != "win32":
            # Make executable on Unix
            script_path.chmod(0o755)
        
        self.print_success(f"Created startup script: {script_path.name}")
        return True
    
    def create_readme(self):
        """Create README with instructions"""
        readme_content = f"""# {self.project_name}

A {self.framework.capitalize()} project with TailwindCSS, created using Django DevTool.

## 🚀 Quick Start

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./start.sh
```

Or manually:
```bash
# Activate virtual environment
# Windows
{self.venv_name}\\Scripts\\activate

# Linux/Mac
source {self.venv_name}/bin/activate

# Run server
cd mysite
python manage.py runserver
```

## 📁 Project Structure

```
{self.project_name}/
├── {self.venv_name}/              # Virtual environment
├── mysite/                        # Django project
│   ├── mysite/                    # Project settings
│   ├── theme/                     # Theme app (TailwindCSS)
│   │   └── static/src/
│   │       ├── input.css          # Tailwind input
│   │       └── output.css         # Tailwind output (generated)
│   └── web/                       # Web app
│       ├── views.py
│       └── templates/
├── node_modules/                  # NPM packages
├── package.json                   # NPM configuration
├── tailwind.config.js             # Tailwind configuration
└── start.{('bat' if sys.platform == 'win32' else 'sh')}                   # Startup script
```

## 🎨 TailwindCSS

TailwindCSS is configured to watch for changes automatically when DEBUG=True.

The watcher compiles:
- Input: `theme/static/src/input.css`
- Output: `theme/static/src/output.css`

## 📦 Installed Packages

### Python
- {self.framework}
- django-livereload-server

### NPM
- tailwindcss
- @tailwindcss/cli

## 🔧 Development

Visit http://127.0.0.1:8000 to see your site.

The admin panel is at http://127.0.0.1:8000/admin

## 📚 Documentation

- [{self.framework.capitalize()}](https://{'docs.wagtail.org' if self.framework == 'wagtail' else 'docs.djangoproject.com'})
- [TailwindCSS](https://tailwindcss.com/docs)

---
Created with Django DevTool 🛠️
"""
        
        readme_path = self.project_root / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        self.print_success("Created README.md")
        return True
    
    def check_prerequisites(self):
        """Check if all required tools are installed"""
        self.print_header("🔍 Checking Prerequisites")
        
        all_good = True
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            self.print_success(f"Python {python_version} found")
        except:
            self.print_error("Python not found")
            all_good = False
        
        # Check npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=(platform.system() == "Windows"))
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                self.print_success(f"npm {npm_version} found")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.print_error("npm not found!")
            self.print_error("Please install Node.js and npm from: https://nodejs.org/")
            all_good = False
        
        # Check Git (optional but recommended)
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                git_version = result.stdout.strip().split()[-1]
                self.print_success(f"Git {git_version} found")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.print_warning("Git not found (optional, but recommended for Windows)")
            if sys.platform == "win32":
                self.print_info("Install Git Bash from: https://git-scm.com/downloads")
        
        if not all_good:
            self.print_error("\n❌ Missing required prerequisites. Please install them and try again.")
            return False
        
        self.print_success("\n✅ All prerequisites met!")
        return True
    
    def run(self):
        """Execute the complete setup process"""
        # Check prerequisites first
        if not self.check_prerequisites():
            return False
        
        steps = [
            ("Creating project structure", self.create_project_structure),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Initializing NPM and TailwindCSS", self.initialize_npm),
            ("Creating TailwindCSS configuration", self.create_tailwind_config),
            ("Creating Django/Wagtail project", self.create_django_project),
            ("Creating theme app", self.create_theme_app),
            ("Creating web app", self.create_web_app),
            ("Configuring settings", self.configure_settings),
            ("Configuring URLs", self.create_urls),
            # ("Creating startup scripts", self.create_startup_script),
            ("Creating README", self.create_readme),
        ]
        
        total_steps = len(steps)
        
        for i, (description, func) in enumerate(steps, 1):
            print(f"\n{Colors.BOLD}[{i}/{total_steps}] {description}...{Colors.ENDC}")
            if not func():
                self.print_error(f"Failed at step: {description}")
                return False
        
        self.print_final_message()
        return True
    
    def print_final_message(self):
        """Print final success message with instructions"""
        print(f"\n{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 SUCCESS! Project created successfully!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}📁 Project location:{Colors.ENDC} {self.project_root}")
        print(f"{Colors.BOLD}🌐 Framework:{Colors.ENDC} {self.framework.capitalize()}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. cd {self.project_name}")
        
        if sys.platform == "win32":
            print(f"  2. start.bat")
        else:
            print(f"  2. ./start.sh")
        
        print(f"  3. Open http://127.0.0.1:8000 in your browser")
        print(f"\n{Colors.OKCYAN}Happy coding! 🚀{Colors.ENDC}\n")


def main():
    """Main entry point for the DevTool"""
    parser = argparse.ArgumentParser(
        description="Django/Wagtail DevTool - Automated project setup with TailwindCSS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s myproject                    # Create a Wagtail project
  %(prog)s myproject --django           # Create a Django project
  %(prog)s myproject --venv env         # Use custom venv name
  %(prog)s myproject --django --venv .venv
        """
    )
    
    parser.add_argument(
        "project_name",
        help="Name of the project to create"
    )
    
    parser.add_argument(
        "--django",
        action="store_true",
        help="Use Django instead of Wagtail (default: Wagtail)"
    )
    
    parser.add_argument(
        "--venv",
        default="venv",
        help="Name of the virtual environment directory (default: venv)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Django DevTool 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Determine framework
    framework = "django" if args.django else "wagtail"
    
    # Create and run DevTool
    devtool = DevTool(
        project_name=args.project_name,
        framework=framework,
        venv_name=args.venv
    )
    
    try:
        success = devtool.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()