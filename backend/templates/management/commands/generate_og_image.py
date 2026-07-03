"""
Génère l'image de partage du site (Open Graph, 1200×630) à partir du modèle
vedette « Prestige Orange » : c'est ce CV qui apparaît quand on partage le lien
du site sur WhatsApp, Facebook, LinkedIn, etc.

Usage : python manage.py generate_og_image
Sortie : frontend/public/og-cv.png (servie à la racine du site).
"""
import io
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageFilter

from cvs.renderers.html import render_html_template_preview_png_bytes
from templates.management.commands.seed_catalog import COMPTABLE, photo
from templates.models import CVTemplate

OG_SIZE = (1200, 630)
BACKGROUND = "#e9f5ee"  # émeraude clair, identité du site


class Command(BaseCommand):
    help = "Génère frontend/public/og-cv.png depuis le modèle vedette Prestige Orange."

    def handle(self, *args, **options):
        # Instance non persistée : seul le slug sert à résoudre le renderer.
        template = CVTemplate(slug="prestige-orange", name="Prestige Orange", category="creative")
        data = dict(COMPTABLE)
        data["photo_url"] = photo(2)
        png = render_html_template_preview_png_bytes(template, data, base_name="og-cv")

        cv_image = Image.open(io.BytesIO(png)).convert("RGB")
        cv_height = 566
        cv_width = round(cv_image.width * cv_height / cv_image.height)
        cv_image = cv_image.resize((cv_width, cv_height), Image.LANCZOS)
        left = (OG_SIZE[0] - cv_width) // 2
        top = (OG_SIZE[1] - cv_height) // 2

        canvas = Image.new("RGBA", OG_SIZE, BACKGROUND)
        shadow = Image.new("RGBA", OG_SIZE, (0, 0, 0, 0))
        shadow.paste(Image.new("RGBA", (cv_width + 16, cv_height + 16), (13, 42, 30, 110)), (left - 4, top + 4))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        canvas = Image.alpha_composite(canvas, shadow)
        canvas.paste(cv_image, (left, top))

        output = Path(settings.BASE_DIR).parent / "frontend" / "public" / "og-cv.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(output, "PNG", optimize=True)
        self.stdout.write(self.style.SUCCESS(f"Image Open Graph générée : {output}"))
