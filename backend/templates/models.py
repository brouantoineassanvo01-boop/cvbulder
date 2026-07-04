from django.db import models


class CVTemplate(models.Model):
    """
    Modèle de CV professionnel avec aperçu multi-résolution.
    
    Champs:
    - name: Nom du template (ex: "Classique Élégant")
    - slug: Identifiant URL unique
    - description: Description courte du template
    - long_description: Description détaillée et avantages
    - category: Catégorie du template (classique, moderne, créatif, etc.)
    - thumbnail: Image miniature (200x280px) pour la grille
    - preview_full: Image d'aperçu haute résolution (1200x1697px A4)
    - docx_filename: Fichier Word source dans cvs/docx_templates/
    - is_premium: Si le template est réservé aux utilisateurs premium
    - order: Ordre d'affichage
    - is_active: Si le template est disponible
    """
    CATEGORY_CHOICES = [
        ("classic", "Classique"),
        ("modern", "Moderne"),
        ("creative", "Créatif"),
        ("minimal", "Minimaliste"),
        ("colorful", "Coloré"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(help_text="Description courte (1-2 lignes)")
    long_description = models.TextField(blank=True, help_text="Description détaillée et avantages")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="classic")
    
    # Images d'aperçu
    thumbnail = models.ImageField(
        upload_to="templates/thumbnails/",
        blank=True,
        null=True,
        help_text="Image miniature pour la grille (200x280px)"
    )
    preview_full = models.ImageField(
        upload_to="templates/previews/",
        blank=True,
        null=True,
        help_text="Aperçu haute résolution (1200x1697px A4)"
    )
    
    # Ancien champ conservé pour retrocompatibilité
    preview_image_url = models.URLField(blank=True, null=True)
    
    # Fichier Word source
    docx_filename = models.CharField(max_length=255, blank=True, null=True)
    
    # Statut
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Si désactivé, le template ne s'affiche pas")
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage (0=premier)")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Template CV"
        verbose_name_plural = "Templates CV"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def _static_preview_url(self):
        """Aperçu embarqué dans l'image Docker (`backend/static/templates/previews/`).
        Sert de repli quand les fichiers médias ont disparu : les hébergements sans
        disque persistant (plan gratuit Render) perdent le dossier media à chaque
        redémarrage, alors que les statiques sont figés dans l'image."""
        relative = f"templates/previews/{self.slug}.png"
        try:
            from django.contrib.staticfiles.storage import staticfiles_storage

            if staticfiles_storage.exists(relative):
                return staticfiles_storage.url(relative)
        except Exception:
            pass
        try:
            from django.contrib.staticfiles.finders import find
            from django.templatetags.static import static as static_url

            if find(relative):
                return static_url(relative)
        except Exception:
            pass
        return ""

    @staticmethod
    def _file_exists(field):
        """Vrai si le champ fichier pointe vers un fichier réellement présent."""
        try:
            return bool(field) and field.storage.exists(field.name)
        except Exception:
            return False

    @property
    def preview_url(self):
        """URL de l'aperçu (priorité: preview_full > thumbnail > statique embarqué > preview_image_url).
        Les fichiers manquants sur le disque sont ignorés au profit du repli statique."""
        if self._file_exists(self.preview_full):
            return self.preview_full.url
        if self._file_exists(self.thumbnail):
            return self.thumbnail.url
        static = self._static_preview_url()
        if static:
            return static
        return self.preview_image_url or ""

    @property
    def thumbnail_url(self):
        """Retourne l'URL de la miniature"""
        if self._file_exists(self.thumbnail):
            return self.thumbnail.url
        return self.preview_url
