"""Tests de l'outil de dépôt de justificatifs."""
import asyncio, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import httpx
from pennylane_mcp import api

captured = {}

def handler(request: httpx.Request) -> httpx.Response:
    captured["url"] = str(request.url)
    captured["ct"] = request.headers.get("content-type", "")
    captured["auth"] = request.headers.get("authorization", "")
    captured["body"] = request.content
    return httpx.Response(200, json={"id": 4242, "filename": "facture.pdf"})

async def main():
    ok = True
    # client "résolu" simulé, avec l'en-tête JSON par défaut du serveur
    fake = httpx.AsyncClient(
        base_url="https://app.pennylane.com/api/external/v2",
        headers={"Content-Type": "application/json", "Authorization": "Bearer TEST_TOKEN"},
        transport=httpx.MockTransport(handler),
    )
    api._client = fake
    async def _resolve(slug=None): return fake
    api._resolve_client = _resolve

    # 1. requête multipart bien formée
    res = await api.api_post_multipart(
        "/ledger_attachments",
        files={"file": ("facture.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    t1 = res == {"id": 4242, "filename": "facture.pdf"}
    t2 = captured["url"].endswith("/ledger_attachments")
    t3 = captured["ct"].startswith("multipart/form-data; boundary=")
    t4 = captured["auth"] == "Bearer TEST_TOKEN"
    t5 = b"facture.pdf" in captured["body"] and b"%PDF-1.4 fake" in captured["body"]
    for n, t in [("réponse JSON parsée", t1), ("bon endpoint", t2),
                 ("Content-Type multipart (pas json)", t3),
                 ("Authorization repris", t4), ("fichier dans le corps", t5)]:
        print(("  ✅ " if t else "  ❌ ") + n); ok &= t

    # 2. validations locales de l'outil
    from mcp.server.fastmcp import FastMCP
    from pennylane_mcp.tools import attachments
    m = FastMCP("test"); attachments.register(m)
    tools = {t.name for t in await m.list_tools()}
    t6 = {"pennylane_upload_attachment", "pennylane_get_attachment"} <= tools
    print(("  ✅ " if t6 else "  ❌ ") + f"outils enregistrés ({len(tools)} exposés)"); ok &= t6

    async def call(**kw):
        return await m.call_tool("pennylane_upload_attachment", kw)

    r = await call(file_path="/nexistepas/x.pdf")
    t7 = "introuvable" in str(r)
    print(("  ✅ " if t7 else "  ❌ ") + "fichier manquant → erreur claire"); ok &= t7

    with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
        f.write(b"x"); bad = f.name
    r = await call(file_path=bad)
    t8 = "non prise en charge" in str(r)
    print(("  ✅ " if t8 else "  ❌ ") + "extension refusée"); ok &= t8
    os.unlink(bad)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        empty = f.name
    r = await call(file_path=empty)
    t9 = "vide" in str(r)
    print(("  ✅ " if t9 else "  ❌ ") + "fichier vide refusé"); ok &= t9
    os.unlink(empty)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4 contenu"); good = f.name
    r = await call(file_path=good)
    t10 = "déposé" in str(r) and "4242" in str(r)
    print(("  ✅ " if t10 else "  ❌ ") + "upload nominal"); ok &= t10
    os.unlink(good)

    print("\n" + ("TOUS LES TESTS PASSENT" if ok else "ÉCHEC"))
    return 0 if ok else 1

sys.exit(asyncio.run(main()))
