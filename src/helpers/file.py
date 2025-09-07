import json
from pathlib import Path

import aiofiles


async def load_from_json(file_path: str):
    async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)


def get_file_paths(directory_path: Path, extension: str) -> list[str]:
    return directory_path.glob(f"*.{extension}")
