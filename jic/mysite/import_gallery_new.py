import os
import django
from django.core.files import File
import mimetypes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')
django.setup()

from web.models import Gallery, GalleryImage
from wagtail.images.models import Image as WagtailImage
from wagtail.models import Collection
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

gallery, created = Gallery.objects.get_or_create(title='Galería Principal')

print('Eliminando imágenes con categoría General o general...')
GalleryImage.objects.filter(category__iexact='General').delete()

# Get or create "Fotos" root collection
root_collection = Collection.get_first_root_node()
try:
    fotos_collection = Collection.objects.child_of(root_collection).get(name='Fotos')
except Collection.DoesNotExist:
    # If using paths instead of direct tree, safe approach:
    # check if 'Fotos' exists first:
    pass

fotos_qs = Collection.objects.filter(name='Fotos')
if not fotos_qs.exists():
    fotos_collection = root_collection.add_child(name='Fotos')
else:
    fotos_collection = fotos_qs.first()


base_dir = "mysite/FOTOS-JIC"

folders_to_process = [
    'JIC-APANAC-2023',
    'FOTOS-SENACYT-UTP-UMECIT-2024',
    'FOTOS-DICOMES-JIC-APANAC-2025',
    '2025.10.01 JIC GRAN FINAL'
]

for folder_name in folders_to_process:
    root = os.path.join(base_dir, folder_name)
    if not os.path.exists(root):
        print(f"Directorio no existe: {root}")
        continue

    print(f'Procesando carpeta: {folder_name}')
    
    # Determine year
    if '2023' in folder_name:
        year = '2023'
    elif '2024' in folder_name:
        year = '2024'
    elif '2025' in folder_name:
        year = '2025'
    else:
        year = '2025' # Fallback
        
    year_int = int(year)
    
    # Description
    if year_int % 2 != 0:
        desc = f"JIC APANAC {year}"
    else:
        desc = f"JIC SENACYT IESTEC {year}"
        
    # Collection
    collection_name = str(year)
    year_coll_qs = Collection.objects.child_of(fotos_collection).filter(name=collection_name)
    if not year_coll_qs.exists():
        year_collection = fotos_collection.add_child(name=collection_name)
    else:
        year_collection = year_coll_qs.first()
        
    # Tags
    tags = [str(year)]
    if 'APANAC' in folder_name or year_int % 2 != 0:
        tags.append('APANAC')
    if 'IESTEC' in folder_name or year_int % 2 == 0:
        tags.append('IESTEC')

    category_name = str(year)
    
    # Also iterate inside the folder if it has subfolders or just files.
    for root_dir, dirs, files in os.walk(root):
        for file_name in files:
            file_path = os.path.join(root_dir, file_name)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('image/'):
                with open(file_path, 'rb') as f:
                    file_title = f'{folder_name} - {file_name}'
                    
                    if WagtailImage.objects.filter(title=file_title).exists():
                        print(f'{file_name} ya existe. Saltando.')
                        # Update description, category, tags for existing ones too? Prompt: agrega las fotos
                        continue
                    
                    wagtail_img = WagtailImage(
                        title=file_title,
                        file=File(f, name=file_title),
                        uploaded_by_user=admin_user,
                        collection=year_collection,
                    )
                    wagtail_img.save()
                    wagtail_img.tags.add(*tags)
                    wagtail_img.save()
                    
                    GalleryImage.objects.create(
                        gallery=gallery,
                        image=wagtail_img,
                        category=category_name,
                        description=desc,
                        alt_text=file_title
                    )
                    print(f'Agregada {file_name}')

print('¡Hecho!')