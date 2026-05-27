import os
import zipfile
import logging

logger = logging.getLogger(__name__)


def resolve_safe_path(base_dir: str, user_input: str) -> str:
    """Resolve a user-supplied path within a base directory."""
    resolved = os.path.realpath(os.path.join(base_dir, user_input))
    if not resolved.startswith(os.path.realpath(base_dir)):
        raise ValueError(f"Access denied: path resolves outside '{base_dir}'")
    return resolved


def extract_archive(zip_path: str, dest_dir: str) -> list:
    """Extract a zip archive into dest_dir."""
    extracted = []
    real_dest = os.path.realpath(dest_dir)
    with zipfile.ZipFile(zip_path) as zf:
        for entry in zf.infolist():
            target = os.path.realpath(os.path.join(dest_dir, entry.filename))
            if not target.startswith(real_dest + os.sep):
                raise Exception(
                    f"Blocked: entry '{entry.filename}' resolves outside destination"
                )
            zf.extract(entry, dest_dir)
            extracted.append(target)
    return extracted


def safe_filename(filename: str) -> str:
    """Return a sanitized version of a user-supplied filename."""
    parts = filename.replace('\\', '/').split('/')
    if '..' in parts:
        raise ValueError(f"Invalid filename: '{filename}'")
    return os.path.basename(filename)
