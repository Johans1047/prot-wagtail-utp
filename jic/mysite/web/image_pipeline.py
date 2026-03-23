from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image as PilImage, ImageOps


RASTER_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}


@dataclass
class ImageOptimizationResult:
    replace_file: bool
    content: bytes | None
    extension: str | None
    final_size: int
    width: int | None
    height: int | None


def _replace_extension(file_name: str, new_ext: str | None) -> str:
    if not new_ext:
        return file_name
    return str(Path(file_name).with_suffix(new_ext))


def _normalize_source_format(field_file, image: PilImage.Image) -> str:
    source_format = (image.format or "").upper()
    if source_format:
        return source_format

    ext = Path(getattr(field_file, "name", "")).suffix.lower()
    return {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
    }.get(ext, "")


def _target_format(source_format: str) -> str:
    if source_format in {"JPEG", "JPG"}:
        return "JPEG"

    if source_format == "PNG" and bool(getattr(settings, "IMAGE_COMPRESSION_CONVERT_PNG_TO_WEBP", True)):
        return "WEBP"

    return source_format


def _prepare_mode(image: PilImage.Image, target_format: str) -> PilImage.Image:
    if target_format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
        return image.convert("RGB")

    if target_format in {"WEBP", "PNG"} and image.mode == "P":
        return image.convert("RGBA")

    return image


def _encode_image(image: PilImage.Image, target_format: str, quality: int) -> bytes:
    output = BytesIO()

    if target_format == "JPEG":
        image.save(output, format="JPEG", quality=quality, optimize=True, progressive=True)
    elif target_format == "WEBP":
        image.save(output, format="WEBP", quality=quality, method=6)
    else:
        image.save(output, format="PNG", optimize=True, compress_level=9)

    return output.getvalue()


def optimize_uploaded_raster_image(field_file) -> ImageOptimizationResult | None:
    if not field_file:
        return None

    max_source_size = int(getattr(settings, "IMAGE_MAX_SOURCE_SIZE", 25 * 1024 * 1024))
    max_final_size = int(getattr(settings, "IMAGE_MAX_FINAL_SIZE", 5 * 1024 * 1024))
    max_dimension = int(getattr(settings, "IMAGE_COMPRESSION_MAX_DIMENSION", 2560))
    quality_steps = tuple(getattr(settings, "IMAGE_COMPRESSION_QUALITY_STEPS", (86, 80, 74, 68, 62, 56, 50, 44)))
    scale_steps = tuple(getattr(settings, "IMAGE_COMPRESSION_SCALE_STEPS", (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)))

    try:
        original_size = int(field_file.size)
    except Exception:
        original_size = 0

    if original_size > max_source_size:
        raise ValidationError(
            f"La imagen excede el tamaño máximo permitido para subir ({max_source_size // (1024 * 1024)} MB)."
        )

    try:
        field_file.open("rb")
        with PilImage.open(field_file) as source_image:
            source_format = _normalize_source_format(field_file, source_image)
            if source_format not in RASTER_FORMATS:
                if original_size > max_final_size:
                    raise ValidationError("Solo se aceptan imágenes de hasta 5 MB.")
                return None

            image = ImageOps.exif_transpose(source_image)
            target_format = _target_format(source_format)
            image = _prepare_mode(image, target_format)

            if max(image.size) > max_dimension:
                image.thumbnail((max_dimension, max_dimension), PilImage.Resampling.LANCZOS)

            best_candidate: tuple[bytes, int, int] | None = None

            for scale in scale_steps:
                if scale <= 0:
                    continue

                working = image.copy()
                if scale < 1.0:
                    scaled_width = max(1, int(working.width * scale))
                    scaled_height = max(1, int(working.height * scale))
                    working = working.resize((scaled_width, scaled_height), PilImage.Resampling.LANCZOS)

                if target_format == "PNG":
                    encoded = _encode_image(working, target_format, quality_steps[0])
                    if len(encoded) <= max_final_size:
                        return ImageOptimizationResult(
                            replace_file=len(encoded) < original_size,
                            content=encoded,
                            extension={"JPEG": ".jpg", "WEBP": ".webp", "PNG": ".png"}[target_format],
                            final_size=len(encoded) if len(encoded) < original_size else original_size,
                            width=working.width,
                            height=working.height,
                        )
                    if best_candidate is None or len(encoded) < len(best_candidate[0]):
                        best_candidate = (encoded, working.width, working.height)
                    continue

                for quality in quality_steps:
                    encoded = _encode_image(working, target_format, quality)
                    if len(encoded) <= max_final_size:
                        return ImageOptimizationResult(
                            replace_file=len(encoded) < original_size,
                            content=encoded,
                            extension={"JPEG": ".jpg", "WEBP": ".webp", "PNG": ".png"}[target_format],
                            final_size=len(encoded) if len(encoded) < original_size else original_size,
                            width=working.width,
                            height=working.height,
                        )

                    if best_candidate is None or len(encoded) < len(best_candidate[0]):
                        best_candidate = (encoded, working.width, working.height)

            if original_size <= max_final_size:
                return ImageOptimizationResult(
                    replace_file=False,
                    content=None,
                    extension=None,
                    final_size=original_size,
                    width=image.width,
                    height=image.height,
                )

            if best_candidate:
                compressed_size = len(best_candidate[0])
                if compressed_size <= max_final_size:
                    return ImageOptimizationResult(
                        replace_file=compressed_size < original_size,
                        content=best_candidate[0],
                        extension={"JPEG": ".jpg", "WEBP": ".webp", "PNG": ".png"}[target_format],
                        final_size=compressed_size,
                        width=best_candidate[1],
                        height=best_candidate[2],
                    )

            raise ValidationError("No se pudo comprimir la imagen por debajo de 5 MB. Intenta con otra imagen.")
    finally:
        try:
            if hasattr(field_file, "seek"):
                field_file.seek(0)
            elif getattr(field_file, "file", None) and hasattr(field_file.file, "seek"):
                field_file.file.seek(0)
        except Exception:
            pass


def optimize_and_apply_to_field_file(field_file) -> ImageOptimizationResult | None:
    result = optimize_uploaded_raster_image(field_file)
    if not result:
        return None

    if result.replace_file and result.content and result.extension:
        save_name = _replace_extension(field_file.name, result.extension)
        field_file.save(save_name, ContentFile(result.content), save=False)
        result.final_size = len(result.content)

    return result
