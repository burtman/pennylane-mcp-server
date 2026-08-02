# 🧾 Pennylane MCP Server

**⚠️ DISCLAIMER IMPORTANT** — Ce projet est une implémentation personnelle et éducative **non-officielle** du protocole MCP pour Pennylane. Ce n'est pas un produit Pennylane, ni approuvé ou maintenu par Pennylane.

- **Lien officiel** : Pour l'intégration officielle Pennylane, consultez [https://www.pennylane.com](https://www.pennylane.com)
- **Statut** : Projet éducatif à titre personnel
- **Licence** : MIT

---

## À propos

Serveur MCP (Model Context Protocol) conçu à des fins éducatives pour exposer l'API comptable **Pennylane V2** sous forme d'outils utilisables par des LLM compatibles (Claude, GPT, Mistral, etc.).

[Installation](#installation) • [Configuration](#configuration) • [Fonctionnalités](#fonctionnalités) • [Utilisation](#utilisation)

---

## ⚖️ Avertissement Légal

### Statut du projet

Ce projet est :
- ✅ **Éducatif** — Créé pour apprendre et explorer le protocole MCP
- ✅ **Personnel** — Développement indépendant sans but commercial
- ✅ **Non-officiel** — Aucune affiliation avec Pennylane SAS
- ❌ **Non commercialisé** — N'utiliser que pour usage personnel/interne
- ❌ **Non soutenu par Pennylane** — Aucun support officiel

### Conditions d'utilisation

Cet outil est fourni **tel quel** (as-is) sans garantie. L'utilisateur est seul responsable de :

1. **Conformité légale** — Respecter les conditions d'utilisation de l'API Pennylane
2. **Sécurité** — Protéger les tokens API et les données comptables confidentielles
3. **Validation** — Vérifier les opérations (écritures, factures, lettrage) avant toute production
4. **Responsabilité** — Assumer l'entière responsabilité des impacts sur vos données comptables

### Relation avec Pennylane

- Ce projet utilise l'API publique de Pennylane dans le respect de leurs conditions d'utilisation
- Les droits d'auteur et les marques commerciales **Pennylane** appartiennent à Pennylane SAS
- Aucun code interne, aucun secret commercial, aucune propriété intellectuelle Pennylane n'a été utilisé
- Ce projet est fourni à titre éducatif et n'a pas vocation à concurrencer les services Pennylane

### Acceptation des risques

En utilisant ce projet, vous acceptez :
- Les risques liés à une implémentation non-officielle
- L'absence de support, de maintenance, ou de garantie
- Que Pennylane ne soit en aucun cas responsable des dysfonctionnements ou pertes de données

---

## Présentation

**Pennylane MCP Server** expose une sélection de l'API Pennylane V2 sous forme d'**87 outils MCP** utilisables par n'importe quel LLM compatible.

Il permet d'automatiser des opérations comptables répétitives : consultation du plan comptable, saisie d'écritures, lettrage, balance générale, gestion des factures, devis, et plus.

**Support multi-dossiers** : Gérez plusieurs dossiers comptables simultanément et basculez entre clients à la volée.

### Pourquoi ce projet ?

Les experts-comptables passent un temps considérable sur des tâches répétitives. Ce serveur MCP permet de :

- **Gagner du temps** en automatisant la saisie et la consultation via le langage naturel
- **Gérer un portefeuille clients** en basculant entre dossiers sans changer d'outil
- **Fiabiliser** grâce à une validation stricte des données (Pydantic v2)
- **Consolider** les données en interrogeant plusieurs dossiers en parallèle

### Qu'est-ce que MCP ?

Le [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) est un protocole ouvert qui permet aux modèles de langage d'interagir avec des outils et des sources de données externes de manière standardisée.

---

## Prérequis

- **Python** >= 3.11
- **pip** (gestionnaire de paquets Python)
- Un ou plusieurs **tokens API Pennylane** (Company Token)

### Obtenir un token API Pennylane

1. Connectez-vous à [Pennylane](https://app.pennylane.com)
2. Allez dans **Paramètres > Connectivité > Développeurs**
3. Générez un **Company API Token** avec les scopes nécessaires :
   - `ledger_accounts:all` — Comptes
   - `journals:all` — Journaux
   - `ledger_entries:all` — Écritures
   - `trial_balance:readonly` — Balance
   - `fiscal_years:readonly` — Exercices
   - `customers:all` — Clients
   - `supplier_invoices:all` — Factures fournisseurs
   - `customer_invoices:all` — Factures clients

> Répétez pour chaque dossier client si vous utilisez le mode multi-dossiers.

---

## Installation

```bash
# 1. Clonez le dépôt
git clone https://github.com/melvynBuilds/pennylane-mcp-server.git
cd pennylane-mcp-server

# 2. (Recommandé) Créez un environnement virtuel
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

# 3. Installez le paquet
pip install -e .
```

---

## Configuration

Le serveur supporte trois modes de fonctionnement, détectés automatiquement au démarrage.

### Mode 1 : Mono-dossier (le plus simple)

Idéal si vous ne gérez qu'un seul dossier Pennylane.

Configurez votre token via une variable d'environnement :

```bash
export PENNYLANE_API_TOKEN="votre_token_pennylane"
```

Ou copiez le fichier `.env.example` :

```bash
cp .env.example .env
# Éditez .env et renseignez votre token
```

### Mode 2 : Multi-dossiers (recommandé pour les cabinets)

Créez un fichier `dossiers.json` à la racine du projet :

```json
{
  "version": "1.0",
  "current_dossier": "sarl-dupont",
  "dossiers": [
    {
      "slug": "sarl-dupont",
      "name": "SARL Dupont",
      "token": "votre_token_dupont_ici",
      "notes": "Client principal"
    },
    {
      "slug": "sci-martin",
      "name": "SCI Martin",
      "token": "votre_token_martin_ici",
      "notes": "SCI locative"
    }
  ]
}
```

> ⚠️ **Ce fichier contient des tokens sensibles.** Il est automatiquement ignoré par Git (via `.gitignore`). Ne le partagez jamais.

Vous pouvez aussi ajouter des dossiers dynamiquement via l'outil MCP `pennylane_add_dossier` sans éditer le fichier manuellement.

### Mode 3 : Sans configuration initiale

Le serveur peut démarrer sans token ni fichier de configuration. Il attendra l'ajout d'un dossier via l'outil MCP `pennylane_add_dossier`.

### Variables d'environnement

| Variable                | Requis | Description                                              |
| ----------------------- | ------ | -------------------------------------------------------- |
| `PENNYLANE_API_TOKEN`   | Non\*  | Token Bearer (mode mono-dossier)                         |
| `PENNYLANE_CONFIG_PATH` | Non    | Chemin vers `dossiers.json` (défaut : `./dossiers.json`) |

\* Requis uniquement si pas de `dossiers.json`.

---

## Intégration avec Claude Desktop

Ajoutez dans votre fichier de configuration Claude Desktop (`claude_desktop_config.json`) :

### Mono-dossier

```json
{
  "mcpServers": {
    "pennylane": {
      "command": "pennylane-mcp-server",
      "env": {
        "PENNYLANE_API_TOKEN": "votre_token_pennylane"
      }
    }
  }
}
```

### Multi-dossiers

```json
{
  "mcpServers": {
    "pennylane": {
      "command": "pennylane-mcp-server",
      "env": {
        "PENNYLANE_CONFIG_PATH": "/chemin/vers/votre/dossiers.json"
      }
    }
  }
}
```

> **Où trouver ce fichier ?**
> - macOS : `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows : `%APPDATA%\Claude\claude_desktop_config.json`

---

## Utilisation

### Lancement direct

```bash
# Multi-dossiers (dossiers.json dans le répertoire courant)
pennylane-mcp-server

# Mono-dossier
PENNYLANE_API_TOKEN=votre_token pennylane-mcp-server

# Via Python directement
python -m pennylane_mcp.server
```

### Exemples de requêtes via LLM

Une fois le serveur connecté à votre LLM, vous pouvez interagir en langage naturel :

**Gestion des dossiers :**
> « Liste-moi tous les dossiers configurés »
> « Bascule sur le dossier SCI Martin »
> « Ajoute le dossier EURL Bernard avec ce token : pl_xxx... »

**Requête multi-dossiers :**
> « Compare la balance générale de tous mes clients sur janvier 2025 »

**Plan comptable :**
> « Montre-moi tous les comptes clients (411) »

**Écriture comptable :**
> « Passe une écriture de vente : 1 200 EUR TTC (1 000 HT + 200 TVA) pour le client DUPONT »

**Balance générale :**
> « Donne-moi la balance générale du 1er janvier au 31 mars 2025 »

**Lettrage :**
> « Lettre le règlement de 1 200 EUR avec la facture correspondante sur le compte 411001 »

**Factures clients :**
> « Crée une facture pour le client Dupont : prestation de conseil, 2 000 EUR HT, TVA 20% »

**Devis :**
> « Crée un devis pour le client Martin pour une mission d'audit à 5 000 EUR HT »

---

## Fonctionnalités

### Gestion multi-dossiers

| Outil                           | Description                                          |
| ------------------------------- | ---------------------------------------------------- |
| `pennylane_list_dossiers`       | Lister tous les dossiers configurés (tokens masqués) |
| `pennylane_current_dossier`     | Afficher le dossier actif + vérification connexion   |
| `pennylane_switch_dossier`      | Basculer vers un autre dossier client                |
| `pennylane_add_dossier`         | Ajouter un dossier (avec validation du token)        |
| `pennylane_remove_dossier`      | Supprimer un dossier de la configuration             |
| `pennylane_multi_dossier_query` | Requête parallèle sur plusieurs dossiers             |

### Plan comptable

| Outil                      | Description                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------ |
| `pennylane_list_accounts`  | Rechercher/lister les comptes (préfixes : 411=clients, 401=fournisseurs, 512=banque) |
| `pennylane_get_account`    | Détail d'un compte                                                                   |
| `pennylane_create_account` | Créer un compte (auto-création client/fournisseur si 411/401)                        |
| `pennylane_update_account` | Modifier libellé ou lettrage                                                         |

### Journaux comptables

| Outil                      | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| `pennylane_list_journals`  | Lister les journaux (ventes, achats, banque, OD, paie) |
| `pennylane_get_journal`    | Détail d'un journal                                    |
| `pennylane_create_journal` | Créer un journal (codes : VE, HA, BQ, OD, PA, RB)      |

### Écritures comptables

| Outil                        | Description                                     |
| ---------------------------- | ----------------------------------------------- |
| `pennylane_list_entries`     | Lister les écritures (filtres journal, période) |
| `pennylane_get_entry`        | Détail complet d'une écriture avec ses lignes   |
| `pennylane_create_entry`     | Passer une écriture équilibrée (débit = crédit) |
| `pennylane_update_entry`     | Modifier une écriture (en-tête + lignes)        |
| `pennylane_list_entry_lines` | Lignes d'une écriture spécifique                |

### Lignes d'écriture et lettrage

| Outil                            | Description                                          |
| -------------------------------- | ---------------------------------------------------- |
| `pennylane_list_all_entry_lines` | Rechercher des lignes (par compte, journal, période) |
| `pennylane_get_entry_line`       | Détail d'une ligne                                   |
| `pennylane_letter_lines`         | Lettrer (rapprocher factures et règlements)          |
| `pennylane_unletter_lines`       | Délettrer                                            |
| `pennylane_link_categories`      | Ventilation analytique (catégories avec poids)       |
| `pennylane_list_line_categories` | Catégories analytiques d'une ligne                   |
| `pennylane_list_lettered_lines`  | Lignes rapprochées ensemble                          |

### Clients et fournisseurs

| Outil                                  | Description                 |
| -------------------------------------- | --------------------------- |
| `pennylane_list_customers`             | Lister les clients          |
| `pennylane_get_customer`               | Détail d'un client          |
| `pennylane_create_company_customer`    | Créer un client entreprise  |
| `pennylane_create_individual_customer` | Créer un client particulier |
| `pennylane_list_suppliers`             | Lister les fournisseurs     |
| `pennylane_get_supplier`               | Détail d'un fournisseur     |
| `pennylane_create_supplier`            | Créer un fournisseur        |

### Factures

| Outil                                 | Description                      |
| ------------------------------------- | -------------------------------- |
| `pennylane_list_customer_invoices`    | Lister les factures clients      |
| `pennylane_get_customer_invoice`      | Détail d'une facture client      |
| `pennylane_create_customer_invoice`   | Créer une facture client         |
| `pennylane_finalize_customer_invoice` | Finaliser un brouillon           |
| `pennylane_list_supplier_invoices`    | Lister les factures fournisseurs |
| `pennylane_get_supplier_invoice`      | Détail d'une facture fournisseur |

### Devis et abonnements

| Outil                                  | Description            |
| -------------------------------------- | ---------------------- |
| `pennylane_list_quotes`                | Lister les devis       |
| `pennylane_get_quote`                  | Détail d'un devis      |
| `pennylane_create_quote`               | Créer un devis         |
| `pennylane_list_billing_subscriptions` | Lister les abonnements |

### Balance, exercices et exports

| Outil                         | Description                                        |
| ----------------------------- | -------------------------------------------------- |
| `pennylane_get_trial_balance` | Balance générale par période                       |
| `pennylane_list_fiscal_years` | Exercices fiscaux et leur statut                   |
| `pennylane_create_fec_export` | Exporter le FEC (Fichier des Écritures Comptables) |
| `pennylane_create_agl_export` | Exporter le Grand Livre Analytique                 |

### Suivi des modifications (Changelogs)

| Outil                                   | Description                                         |
| --------------------------------------- | --------------------------------------------------- |
| `pennylane_changelog_customers`         | Historique des modifications clients                |
| `pennylane_changelog_suppliers`         | Historique des modifications fournisseurs           |
| `pennylane_changelog_products`          | Historique des modifications produits               |
| `pennylane_changelog_customer_invoices` | Historique des modifications factures clients       |
| `pennylane_changelog_supplier_invoices` | Historique des modifications factures fournisseurs  |
| `pennylane_changelog_quotes`            | Historique des modifications devis                  |
| `pennylane_changelog_entry_lines`       | Historique des modifications lignes d'écriture      |
| `pennylane_changelog_transactions`      | Historique des modifications transactions bancaires |

### Utilitaires

| Outil              | Description                                       |
| ------------------ | ------------------------------------------------- |
| `pennylane_whoami` | Vérifier la connexion et les informations société |

---

## Architecture

```
pennylane-mcp-server/
├── pyproject.toml              # Métadonnées et dépendances
├── README.md
├── CLAUDE_CONTEXT.md           # Contexte métier pour le LLM
├── .env.example                # Template de configuration
├── LICENSE                     # Licence MIT
│
└── src/pennylane_mcp/          # Code source
    ├── server.py               # Point d'entrée FastMCP
    ├── constants.py            # URLs, limites, constantes
    ├── models.py               # Modèles Pydantic (validation stricte)
    ├── api.py                  # Client httpx async (multi-dossier aware)
    ├── utils.py                # Formatage, pagination, troncature
    ├── dossier_manager.py      # Gestionnaire multi-dossiers (singleton)
    │
    └── tools/                  # Outils MCP répartis par domaine
        ├── me.py               # Connexion
        ├── accounts.py         # Plan comptable
        ├── journals.py         # Journaux
        ├── entries.py          # Écritures
        ├── entry_lines.py      # Lignes + lettrage + analytique
        ├── trial_balance.py    # Balance + exercices
        ├── customers.py        # Clients
        ├── suppliers.py        # Fournisseurs
        ├── customer_invoices.py # Factures clients
        ├── supplier_invoices.py # Factures fournisseurs
        ├── quotes.py           # Devis
        ├── products.py         # Produits / services
        ├── billing_subscriptions.py # Abonnements
        ├── categories.py       # Catégories analytiques
        ├── exports.py          # Exports FEC / AGL
        ├── changelogs.py       # Journaux de modifications
        └── dossiers.py         # Multi-dossiers

```

---

## Stack technique

| Technologie                                                   | Rôle                           |
| ------------------------------------------------------------- | ------------------------------ |
| [FastMCP](https://github.com/modelcontextprotocol/python-sdk) | Framework MCP Python officiel  |
| [httpx](https://www.python-httpx.org/)                        | Client HTTP asynchrone         |
| [Pydantic v2](https://docs.pydantic.dev/)                     | Validation stricte des entrées |

---

## Comment contribuer

Les contributions sont les bienvenues ! Voici comment étendre le serveur :

1. Créez un modèle Pydantic dans `models.py` pour valider les entrées
2. Créez ou enrichissez un fichier dans `tools/`
3. Décorez votre fonction avec `@mcp.tool(name=..., annotations=...)`
4. Enregistrez le module via `register(mcp)` dans `server.py`

```bash
# Installez en mode développement
pip install -e .

# Testez avec l'inspecteur MCP
mcp dev src/pennylane_mcp/server.py
```

---

## Sécurité

- Les tokens API ne sont **jamais** inclus dans le code source
- Le fichier `dossiers.json` est exclu du dépôt Git via `.gitignore`
- Les tokens sont masqués dans les retours de l'outil `list_dossiers`
- Toutes les entrées utilisateur sont validées par Pydantic v2 (`extra="forbid"`)

---

## Licence

Ce projet est sous licence [MIT](https://github.com/melvynBuilds/pennylane-mcp-server/blob/main/LICENSE).

Cela signifie qu'il peut être utilisé librement à titre éducatif et personnel, sous réserve du respect des conditions d'utilisation de Pennylane.

---

## Support & Ressources

- **Protocole MCP** : https://modelcontextprotocol.io/
- **API Pennylane** : https://www.pennylane.com
- **Issues** : [Dépôt GitHub](https://github.com/melvynBuilds/pennylane-mcp-server/issues)

---

## Auteur

Développé par **Melvyn Morice** — Développeur passionné par l'IA, l'automatisation et la comptabilité.

**Note** : Ce projet est maintenu à titre personnel et éducatif. Il n'est affilié à Pennylane SAS d'aucune manière.
