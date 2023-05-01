from pathlib import Path


def generate_local_file_url(file_path: str) -> str:
    path = Path(file_path).expanduser()
    absolute_file_path = path.resolve()
    local_file_url = f"file://{absolute_file_path}"
    return local_file_url
