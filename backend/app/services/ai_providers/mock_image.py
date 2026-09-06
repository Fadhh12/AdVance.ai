"""Default image provider while no real one is chosen (see `image.py`) — draws a
plain placeholder card with the prompt text on it via Pillow (already a dependency,
pulled in by `qrcode[pil]`). Clearly a mock, not real AI-generated art — same role
`MockVideoProvider` plays for video: exercises the whole pipeline (upload, return a
real usable image) without an API key. Swap for a real provider (Gemini's image
model, Stability, ...) before shipping.
"""
import io
import textwrap
import uuid

from PIL import Image, ImageDraw, ImageFont

from app.services.ai_providers.image import ImageGenerationProvider, ImageGenerationResult
from app.services.storage import upload_object

_SIZE = (1024, 1024)
_BACKGROUND = (27, 29, 40)  # DESIGN_SYSTEM.md --color-panel, not an arbitrary color
_TEXT_COLOR = (237, 238, 243)  # --color-ink


class MockImageProvider(ImageGenerationProvider):
    def generate_image(self, prompt: str) -> ImageGenerationResult:
        image = Image.new("RGB", _SIZE, color=_BACKGROUND)
        draw = ImageDraw.Draw(image)
        wrapped = textwrap.fill(prompt.strip() or "(tanpa prompt)", width=28)
        try:
            font = ImageFont.load_default(size=48)
        except TypeError:  # Pillow <10: load_default() takes no size argument
            font = ImageFont.load_default()

        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=12, align="center")
        position = ((_SIZE[0] - (bbox[2] - bbox[0])) / 2, (_SIZE[1] - (bbox[3] - bbox[1])) / 2)
        draw.multiline_text(
            position, wrapped, fill=_TEXT_COLOR, font=font, align="center", spacing=12
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        key = f"mock-generated/{uuid.uuid4()}.png"
        upload_object(key, buffer, "image/png")
        return ImageGenerationResult(success=True, result_key=key)
