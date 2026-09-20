"""Outils MCP : pièces jointes comptables (justificatifs).

Couvre les deux endpoints ``/ledger_attachments`` de l'API Pennylane V2 :
dépôt d'un fichier et récupération de ses métadonnées.

⚠️ Scopes requis côté token Pennylane :
- ``file_attachments:all`` pour l'upload,
- ``file_attachments:readonly`` (ou ``:all``) pour la lecture.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Annotated, Optional

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from ..api import api_get, api_post_multipart
from ..utils import to_json

# Types acceptés par Pennylane pour un justificatif comptable.
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".heic"}

# Garde-fou : au-delà, l'API refuse le fichier.
MAX_FILE_BYTES = 20 * 1024 * 1024


def register(mcp: FastMCP) -> None:
    """Enregistre les outils de gestion des pièces jointes."""

    # ── Déposer un justificatif ───────────────────────────────────────────────

    @mcp.tool(
        name="pennylane_upload_attachment",
        annotations={
            "title": "Déposer un justificatif",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def pennylane_upload_attachment(
        file_path: Annotated[
            str,
            Field(description="Chemin local du fichier à déposer (PDF ou image)."),
        ],
        dossier_slug: Annotated[
            Optional[str],
            Field(description="Slug du dossier cible. Défaut : dossier actif."),
        ] = None,
        field_name: Annotated[
            str,
            Field(
                description=(
                    "Nom du champ multipart attendu par l'API. Laisser 'file' "
                    "sauf si l'API renvoie une erreur de validation."
                )
            ),
        ] = "file",
    ) -> str:
        """Dépose un justificatif dans le dossier comptable (POST /ledger_attachments).

        Le fichier est envoyé en multipart/form-data. Le justificatif est créé
        sans être rattaché à une écriture : le rapprochement se fait ensuite
        dans Pennylane, ou via les outils d'écritures.

        Nécessite le scope ``file_attachments:all``.
        """
        try:
            path = Path(file_path).expanduser()

            if not path.is_file():
                return f"❌ Fichier introuvable : {path}"

            suffix = path.suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                return (
                    f"❌ Extension non prise en charge : '{suffix}'. "
                    f"Formats acceptés : {', '.join(sorted(ALLOWED_SUFFIXES))}."
                )

            size = path.stat().st_size
            if size == 0:
                return f"❌ Fichier vide : {path.name}"
            if size > MAX_FILE_BYTES:
                return (
                    f"❌ Fichier trop volumineux : {size / 1_048_576:.1f} Mo "
                    f"(maximum {MAX_FILE_BYTES // 1_048_576} Mo)."
                )

            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            content = path.read_bytes()

            data = await api_post_multipart(
                "/ledger_attachments",
                files={field_name: (path.name, content, mime)},
                dossier_slug=dossier_slug,
            )

            return (
                f"✅ Justificatif déposé : {path.name} "
                f"({size / 1024:.0f} Ko, {mime})\n\n{to_json(data)}"
            )
        except Exception as exc:
            return f"❌ {exc}"

    # ── Récupérer un justificatif ─────────────────────────────────────────────

    @mcp.tool(
        name="pennylane_get_attachment",
        annotations={
            "title": "Récupérer un justificatif",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def pennylane_get_attachment(
        id: Annotated[int, Field(description="Identifiant du justificatif.")],
        dossier_slug: Annotated[
            Optional[str],
            Field(description="Slug du dossier cible. Défaut : dossier actif."),
        ] = None,
    ) -> str:
        """Récupère les métadonnées d'un justificatif (GET /ledger_attachments/{id}).

        Retourne notamment le nom du fichier et son URL de téléchargement.

        Nécessite le scope ``file_attachments:readonly`` ou ``:all``.
        """
        try:
            data = await api_get(
                f"/ledger_attachments/{id}",
                dossier_slug=dossier_slug,
            )
            return to_json(data)
        except Exception as exc:
            return f"❌ {exc}"
