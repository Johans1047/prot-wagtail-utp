import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jic.mysite.mysite.settings.dev')
try:
    django.setup()
except Exception as e:
    # If dev settings fail, try production or base through mysite.settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jic.mysite.mysite.settings.base')
    django.setup()

from wagtail.images.models import Image
from jic.mysite.web.models import Gallery

print("--- Checking Image Model Fields ---")
image_fields = [f.name for f in Image._meta.get_fields()]
print(f"Fields in Image model: {image_fields}")

print("\n--- Checking Gallery Data ---")
gallery = Gallery.objects.first()
if gallery:
    print(f"Gallery found: {gallery.title}")
    for item in gallery.gallery_images.all():
        img = item.image
        print(f"\nImage ID: {img.id}")
        print(f"Title: {img.title}")
        
        # Check for description field
        if 'description' in image_fields:
            print(f"Description (field): '{img.description}'")
        else:
            print("Description field NOT FOUND in Image model")
            
        # Check for caption in GalleryImage
        print(f"GalleryItem Caption: '{item.caption}'")
        
        # Retrieve what the view logic does
        description_view = img.description if hasattr(img, 'description') and img.description else ""
        category_view = item.caption if item.caption else "General"
        
        print(f"View Description would be: '{description_view}'")
        print(f"View Category would be: '{category_view}'")
else:
    print("No Gallery found")
