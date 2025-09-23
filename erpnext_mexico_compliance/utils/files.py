"""Copyright (c) 2025, TI Sin Problemas and contributors
For license information, please see license.txt"""

import io
import os
import zipfile


def compress_files(file_paths: list[str]) -> bytes:
    """Compresses a list of file paths into a single ZIP file.

    Args:
        file_paths (list[str]): A list of file paths to be compressed.

    Returns:
        bytes: The compressed ZIP file as bytes.
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for file_path in file_paths:
            z.write(file_path, os.path.basename(file_path))
    return buffer.getvalue()
