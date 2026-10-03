from PIL import Image
import io

MAX_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
TARGET_SIZE_BYTES = 4 * 1024 * 1024  # compress down toward ~4MB if over the cap


def process_image(file_bytes: bytes, filename: str) -> bytes:
    """
    If the uploaded image is under 10MB, returns it unchanged.
    If it's over 10MB, progressively reduces JPEG quality (and if needed,
    resizes dimensions) until it fits under the target size, then returns
    the compressed bytes ready for upload.
    """
    if len(file_bytes) <= MAX_SIZE_BYTES:
        return file_bytes

    image = Image.open(io.BytesIO(file_bytes))

    # Convert to RGB if needed (PNG with alpha, etc. can't always save as JPEG directly)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    quality = 85
    output = io.BytesIO()

    while quality >= 30:
        output.seek(0)
        output.truncate()
        image.save(output, format="JPEG", quality=quality, optimize=True)

        if output.tell() <= TARGET_SIZE_BYTES:
            break

        quality -= 10

    # If quality reduction alone isn't enough, also scale down dimensions
    if output.tell() > TARGET_SIZE_BYTES:
        scale_factor = 0.8
        while output.tell() > TARGET_SIZE_BYTES and scale_factor > 0.3:
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            resized = image.resize((new_width, new_height), Image.LANCZOS)

            output.seek(0)
            output.truncate()
            resized.save(output, format="JPEG", quality=70, optimize=True)
            scale_factor -= 0.1

    output.seek(0)
    return output.read()