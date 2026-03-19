import os
import sys
import django

# Provide the path to the inner mysite directory if needed, or we might need to set it from the terminal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "jic/mysite")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
django.setup()

from django.core.files import File
from wagtail.documents.models import Document
from taggit.models import Tag

base_path = r"C:\Users\jony1\Downloads\Proyectos\jic-utp\ssd jic"

def import_folder(folder_name, tag_name):
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            # Check if document already exists
            if Document.objects.filter(title=filename).exists():
                print(f"Document already exists: {filename}")
                continue
            
            with open(filepath, 'rb') as f:
                doc = Document(title=filename, file=File(f, name=filename))
                doc.save()
                doc.tags.add(tag_name)
                doc.save()
            print(f"Imported {filename} with tag {tag_name}")

if __name__ == '__main__':
    import_folder('Boletines', 'boletin')
    import_folder('Memorias', 'memoria')
    print("Done importing documents.")
