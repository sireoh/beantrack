"""ID generation. All generated IDs are UUID4 strings."""

import uuid


def new_id() -> str:
    return str(uuid.uuid4())
