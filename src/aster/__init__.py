import traceback
from typing import Final

ASTER_ENV_PREFIX: Final[str] = "aster_"
ASTER_VERSION: Final[str] = "0.1.0"

try:
    from aster.auth.models import User as User
    from aster.auth.models import UserBlock as UserBlock
    from aster.posts.models import Post as Post
except Exception:
    traceback.print_exc()
