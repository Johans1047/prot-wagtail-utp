import os
import django
from django.core.files import File
import re
import mimetypes
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')
django.setup()

from web.models import Gallery, GalleryImage
from wagtail.images.models import Image as WagtailImage
from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

gallery, created = Gallery.objects.get_or_create(title='Galería Principal')

base_dir = '/app/mysite/FOTOS-JIC'

for root, dirs, files in os.walk(base_dir):
    folder_name = os.path.basename(root)
    if folder_name == 'FOTOS-JIC': continue
    
    print(f'Procesando carpeta: {folder_name}')
    
    category_name = folder_name
    for file_name in files:
        file_path = os.path.join(root, file_name)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('image/'):
            with open(file_path, 'rb') as f:
                file_title = f'{folder_name} - {file_name}'
                if WagtailImage.objects.filter(title=file_title).exists():
                    print(f'{file_name} ya existe. Saltando.')
                    continue
                
                wagtail_img = WagtailImage(
                    title=file_title,
                    file=File(f, name=file_title),
                    uploaded_by_user=admin_user,
                )
                wagtail_img.save()
                
                GalleryImage.objects.create(
                    gallery=gallery,
                    image=wagtail_img,
                    category=category_name,
                    description=f'Foto de {folder_name}',
                    alt_text=f'Foto {file_name}'
                )
                print(f'Agregada {file_name}')
print('Done.')