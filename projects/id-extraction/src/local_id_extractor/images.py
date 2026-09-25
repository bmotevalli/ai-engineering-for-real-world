"""Bounded decoding and metadata-free in-memory encoding; no temporary images."""
import io
import warnings
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 15 * 1024 * 1024
MAX_PIXELS = 20_000_000


class ImageInputError(ValueError):
    pass


def read_image(source: str | Path | bytes) -> bytes:
    """Read at most the upload limit plus one byte, including in the harness."""
    try:
        if isinstance(source, bytes):
            raw = source
        else:
            with Path(source).open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
        if not raw or len(raw) > MAX_BYTES:
            raise ImageInputError("image must be nonempty and at most 15 MiB")
        return raw
    except OSError:
        raise ImageInputError("cannot read image") from None


def prepare_image(source: str | Path | bytes) -> bytes:
    raw = read_image(source)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise ImageInputError("only PNG, JPEG and WebP images are supported")
                if image.width * image.height > MAX_PIXELS or getattr(image, "n_frames", 1) != 1:
                    raise ImageInputError("image exceeds pixel limit or is animated")
                image.load()
                oriented = ImageOps.exif_transpose(image).convert("RGBA")
                background = Image.new("RGBA", oriented.size, "white")
                background.alpha_composite(oriented)
                clean = background.convert("RGB")
                clean.info.clear()
                output = io.BytesIO()
                clean.save(output, format="PNG")
                encoded = output.getvalue()
                if len(encoded) > MAX_BYTES:
                    raise ImageInputError("decoded image is too large; crop or resize locally")
                return encoded
    except ImageInputError:
        raise
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError,
            Image.DecompressionBombWarning):
        raise ImageInputError("cannot decode a supported image") from None
