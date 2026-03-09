# my_site

A Wagtail project with TailwindCSS, created using Django DevTool.

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
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Run server
cd mysite
python manage.py runserver
```

## 📁 Project Structure

```
my_site/
├── venv/              # Virtual environment
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
└── start.bat                   # Startup script
```

## 🎨 TailwindCSS

TailwindCSS is configured to watch for changes automatically when DEBUG=True.

The watcher compiles:
- Input: `theme/static/src/input.css`
- Output: `theme/static/src/output.css`

## 📦 Installed Packages

### Python
- wagtail
- django-livereload-server

### NPM
- tailwindcss
- @tailwindcss/cli

## 🔧 Development

Visit http://127.0.0.1:8000 to see your site.

The admin panel is at http://127.0.0.1:8000/admin

## 📚 Documentation

- [Wagtail](https://docs.wagtail.org)
- [TailwindCSS](https://tailwindcss.com/docs)

---
Created with Django DevTool 🛠️
