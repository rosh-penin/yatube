import tempfile

from django.conf import settings


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

MULTIPLIER_FOR_EVERYTHING = 15
