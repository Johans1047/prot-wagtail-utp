import os
import sys
import django

# Setup Django environment
sys.path.append('/app/mysite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')
django.setup()

from django.core.files import File
from wagtail.documents.models import Document
from taggit.models import Tag

def import_folder(folder_path, tag_name):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            # Check if document already exists
            if Document.objects.filter(title=filename).exists():
                print(f"Document already exists: {filename}")
                # Optionally add tag if not present
                doc = Document.objects.get(title=filename)
                if tag_name not in [t.name for t in doc.tags.all()]:
                    doc.tags.add(tag_name)
                    doc.save()
                continue
            
            print(f"Importing {filename}...")
            with open(filepath, 'rb') as f:
                doc = Document(title=filename, file=File(f, name=filename))
                doc.save()
                doc.tags.add(tag_name)
                doc.save()
            print(f"Imported {filename} with tag {tag_name}")

if __name__ == '__main__':
    import_folder('/app/boletines', 'boletin')
    import_folder('/app/memorias', 'memoria')
    print("Done importing documents.")
