import io, warnings
from fastapi import HTTPException, UploadFile
from PIL import Image

Image.MAX_IMAGE_PIXELS = 40_000_000
warnings.simplefilter("error", Image.DecompressionBombWarning)


async def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks, total = [], 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(413, f"File too large (max {max_bytes // (1024*1024)}MB)")
        chunks.append(chunk)
    return b"".join(chunks)


def assert_real_image(data: bytes):
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
    except Exception:
        raise HTTPException(400, "File is not a valid image")


def assert_real_video(data: bytes):
    head = data[:12]
    ok = head[4:8] == b"ftyp" or head[:4] == b"\x1a\x45\xdf\xa3"      # mp4/mov or webm
    if not ok:
        raise HTTPException(400, "File is not a valid video")