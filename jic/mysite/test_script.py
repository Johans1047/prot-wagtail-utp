from web.models import CustomImage, CustomRendition
from wagtail.images.models import Filter
import traceback
img = CustomImage.objects.first()
flt = Filter(spec='fill-210x210')
try:
    print("Testing create_rendition...")
    r = img.create_rendition(flt)
    print("Done create_rendition. r.width=", getattr(r, 'width', 'MISSING'))
except Exception as e:
    traceback.print_exc()
