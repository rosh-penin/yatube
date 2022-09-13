import tempfile

from django.conf import settings


# main constants:
CUT_POSTS_NUM: int = 10
PAGES: int = 10
CUT_STR_POST = 15


# constants for tests:
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

MULTIPLIER_FOR_EVERYTHING = 15
