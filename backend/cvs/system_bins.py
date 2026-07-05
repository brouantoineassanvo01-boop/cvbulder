import os
import shutil
from pathlib import Path

from django.conf import settings


def candidate_libreoffice_binaries():
    configured = str(getattr(settings, "LIBREOFFICE_BINARY", "") or "").strip()
    candidates = [configured] if configured else []
    candidates.extend(
        [
            "soffice",
            "libreoffice",
            "/usr/bin/soffice",
            "/usr/bin/libreoffice",
            "/usr/lib/libreoffice/program/soffice",
            "/snap/bin/libreoffice",
            "/var/lib/snapd/snap/bin/libreoffice",
        ]
    )
    found = []
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        resolved = str(path) if path.exists() and os.access(path, os.X_OK) else shutil.which(candidate)
        if resolved and resolved not in found:
            found.append(resolved)
    return found


def libreoffice_not_found_message():
    return (
        "LibreOffice introuvable. Configurez LIBREOFFICE_BINARY avec un chemin valide "
        "ou installez un binaire 'soffice'/'libreoffice'."
    )
