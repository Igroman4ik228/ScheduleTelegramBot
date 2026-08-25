import json
from typing import TYPE_CHECKING

import aiofiles

if TYPE_CHECKING:
    from pathlib import Path


async def load_from_json(file_path: str):
    async with aiofiles.open(file_path, encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)


def get_file_paths(directory_path: Path, extension: str) -> list[Path]:
    return list(directory_path.glob(f"*.{extension}"))
