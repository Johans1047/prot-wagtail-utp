import os
import sys
import django

# Add the project root to the python path
project_root = os.path.join(os.getcwd(), 'jic', 'mysite')
sys.path.append(project_root)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')

try:
    django.setup()
except Exception as e:
    print(f"Dev settings failed: {e}")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.base')
    django.setup()

from web.models import Gallery
from wagtail.images.models import Image

print("--- Checking Gallery Data ---")
gallery = Gallery.objects.first()

if gallery:
    print(f"Gallery: {gallery.title}")
    for item in gallery.gallery_images.all():
        img = item.image
        print(f"\nImage ID: {img.id}")
        print(f"Title: '{img.title}'")
        
        # Check description attribute presence and value
        if hasattr(img, 'description'):
            print(f"Description (attr): '{img.description}'")
        else:
            print("Description attribute MISSING")
            
        print(f"Gallery Item Caption: '{item.caption}'")
else:
    print("No gallery found.")

print("\n--- Checking Random Image directly ---")
img = Image.objects.first()
if img:
    print(f"Image ID: {img.id}")
    if hasattr(img, 'description'):
        print(f"Description: '{img.description}'")
    else:
        print("Description attribute MISSING on standard Image query")
