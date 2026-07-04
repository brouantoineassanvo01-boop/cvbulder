from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import AccessGrant, CV, PaymentTransaction


def _user_admin_link(obj):
    """Lien vers la fiche admin de l'utilisateur (suit l'URL réelle de l'admin)."""
    url = reverse("admin:auth_user_change", args=[obj.user_id])
    return format_html('<a href="{}">{}</a>', url, obj.user)


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    """Suivi complet des CV : contenu, IA, fichiers générés, déblocage."""

    list_display = (
        "title",
        "user_link",
        "template",
        "status",
        "ai_status",
        "is_unlocked",
        "pdf_link",
        "created_at",
        "generated_at",
    )
    list_filter = ("status", "ai_status", "is_unlocked", "template", "template_mode", "created_at")
    search_fields = ("title", "user__username", "user__email", "job_offer_url")
    readonly_fields = ("created_at", "updated_at", "generated_at")
    date_hierarchy = "created_at"
    list_select_related = ("user", "template")
    raw_id_fields = ("user",)
    fieldsets = (
        ("Général", {"fields": ("user", "template", "title", "status", "is_unlocked", "template_mode")}),
        ("Contenu du CV", {"fields": ("data",)}),
        ("Offre d'emploi ciblée", {"fields": ("job_offer_url", "job_offer_text", "job_offer_file"), "classes": ("collapse",)}),
        ("IA", {"fields": ("ai_status", "ai_error", "ai_data", "ai_messages"), "classes": ("collapse",)}),
        ("Fichiers", {"fields": ("source_file", "photo_file", "generated_file", "generated_pdf", "generated_at"), "classes": ("collapse",)}),
        ("Horodatage", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Utilisateur", ordering="user__username")
    def user_link(self, obj):
        return _user_admin_link(obj)

    @admin.display(description="PDF")
    def pdf_link(self, obj):
        if obj.generated_pdf:
            return format_html('<a href="{}" target="_blank">ouvrir</a>', obj.generated_pdf.url)
        return "—"


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Suivi des paiements Paystack. Les identifiants et la réponse brute sont
    en lecture seule pour ne pas casser la réconciliation automatique."""

    list_display = (
        "reference",
        "user_link",
        "plan_type",
        "amount_display",
        "status_badge",
        "paid_at",
        "created_at",
    )
    list_filter = ("plan_type", "status", "currency", "created_at")
    search_fields = ("reference", "user__username", "user__email")
    readonly_fields = ("reference", "authorization_url", "access_code", "raw_response", "created_at", "updated_at", "paid_at")
    date_hierarchy = "created_at"
    list_select_related = ("user", "cv")
    raw_id_fields = ("user", "cv")

    @admin.display(description="Utilisateur", ordering="user__username")
    def user_link(self, obj):
        return _user_admin_link(obj)

    @admin.display(description="Montant", ordering="amount_xof")
    def amount_display(self, obj):
        return f"{obj.amount_xof} {obj.currency}"

    @admin.display(description="Statut", ordering="status")
    def status_badge(self, obj):
        colors = {"success": "#0a7d40", "pending": "#b26a00", "failed": "#b3261e", "cancelled": "#6c757d"}
        color = colors.get(obj.status, "#374151")
        label = obj.get_status_display() if hasattr(obj, "get_status_display") else obj.status
        return format_html('<span style="color:{};font-weight:600;">{}</span>', color, label)


@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    """Droits d'accès (essai, abonnement) : validité et crédits restants."""

    list_display = (
        "user_link",
        "plan_type",
        "active_badge",
        "starts_at",
        "expires_at",
        "cv_credits",
        "ai_credits",
        "created_at",
    )
    list_filter = ("plan_type", "created_at")
    search_fields = ("user__username", "user__email", "cv__title")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "cv")
    raw_id_fields = ("user", "cv", "payment")

    @admin.display(description="Utilisateur", ordering="user__username")
    def user_link(self, obj):
        return _user_admin_link(obj)

    @admin.display(description="État")
    def active_badge(self, obj):
        if obj.expires_at is None or obj.expires_at > timezone.now():
            return format_html('<span style="color:#0a7d40;font-weight:600;">Actif</span>')
        return format_html('<span style="color:#b3261e;">Expiré</span>')
