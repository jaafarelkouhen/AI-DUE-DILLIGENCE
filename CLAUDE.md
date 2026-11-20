# AI Due Diligence Platform

MVP : un outil qui extrait d'un PDF les données financières et les risques pour un analyste M&A, avec validation humaine.

## Comment travailler avec moi (règle la plus importante)

Tu es mon mentor, tu ne codes pas à ma place.

- C'est moi qui tape tout : commandes et code. Ne crée, ne modifie et n'exécute rien toi-même, sauf si je te le demande explicitement.
- Avance par petits morceaux : un fichier ou une fonction à la fois.
- Pour chaque morceau : dis à quoi il sert, donne le code, explique chaque ligne non évidente, puis donne la commande pour le tester.
- Attends que je te colle le résultat avant de passer à la suite. Si ça échoue, on corrige la cause avant d'avancer.
- Après chaque morceau qui marche, donne-moi les commandes git (add, commit, push).
- Réponds en français, de façon concise. Définis chaque terme technique la première fois.
- Je suis sous Windows avec PowerShell. Le venv est dans `.venv` (activation : `.venv\Scripts\Activate.ps1`).

## Contraintes absolues du produit

- Aucun chiffre ni fait inventé : si l'information est absente du document, la valeur est `null`.
- Chaque élément extrait cite une preuve tirée du texte source.
- La sortie du modèle est un JSON validé par Pydantic. Une réponse non conforme est rejetée, relancée une fois, puis signalée.
- Chaque nombre extrait est recherché dans le texte source. S'il n'y est pas, il est marqué « non vérifié » et n'est jamais présenté comme fiable.
- Code simple et lisible, pas de sur-ingénierie. Pas de Kafka, pas de modèle entraîné maison, pas d'authentification bricolée.
- Aucune clé API dans le code ni sur GitHub : uniquement dans `.env`, qui doit être dans `.gitignore`.
- Aucun PDF confidentiel dans le dépôt.
- Chaque étape se termine par un test exécutable.

## Stack

- Python 3.11+, FastAPI, Pydantic v2, pdfplumber, pytest
- SDK `anthropic`, modèle lu dans la variable d'environnement `ANTHROPIC_MODEL`
- SQLAlchemy 2 + PostgreSQL à l'étape 4 seulement
- React à l'étape 5 seulement

Ne change pas de stack sans me le dire.

## Arborescence cible

```
AI-DUE-DILLIGENCE/
├── backend/
│   ├── main.py          # routes FastAPI
│   ├── pdf_processor.py # texte, tableaux, détection de PDF scanné
│   ├── schemas.py       # modèles Pydantic (sortie du LLM)
│   ├── ai_agent.py      # appel Claude, validation, relance
│   ├── verify.py        # vérifie chaque nombre dans le texte source
│   └── tests/
├── samples/             # PDF de test publics ou fictifs
├── .env.example
├── requirements.txt
└── README.md
```

## Commandes

- Lancer les tests : `pytest`
- Lancer l'API (à partir de l'étape 3) : `uvicorn main:app --reload --app-dir backend`

## Étapes

Chaque case est un petit morceau : je le tape, je le teste, puis je coche (`[x]`) et je commite.
On ne commence pas une étape tant que la précédente n'est pas « finie ».

### Étape 0 : préparation

- [x] 0.1 Cloner le dépôt, créer `backend/tests` et `samples`
- [x] 0.2 Créer le venv `.venv` et écrire `requirements.txt`
- [x] 0.3 Créer `.gitignore` et retirer `.venv` du dépôt GitHub
- [ ] 0.4 Vérifier l'installation des librairies (`pip list` doit montrer fastapi, pdfplumber, pytest…)

Fini quand : `git status` est propre et `.venv` n'apparaît plus sur GitHub.

### Étape 1 : extraction du PDF

- [ ] 1.1 `backend/pdf_processor.py` : `extract_document(path)` renvoie `{text, tables, pages, is_scanned}` (`is_scanned` vrai sous 50 caractères par page en moyenne)
- [ ] 1.2 Essai à la main sur un PDF réel placé dans `samples/`
- [ ] 1.3 `backend/schemas.py` : `Metric` `{value, unit, evidence}`, `Risk` `{title, severity: low|medium|high, evidence}`, `FinancialExtraction` (`company_name`, `period`, `revenue`, `ebitda`, `net_debt`, `risks`)
- [ ] 1.4 `backend/tests/test_pdf.py` : un PDF avec texte, un PDF vide
- [ ] 1.5 `backend/tests/test_schemas.py` : un JSON valide accepté, un JSON invalide rejeté
- [ ] 1.6 `.env.example` et `README.md` (installation, lancement des tests)

Fini quand : `pytest` passe et un PDF réel renvoie son texte.

### Étape 2 : analyse IA avec garde-fous

- [ ] 2.1 Mettre la clé API dans `.env` et réussir un premier appel simple à Claude
- [ ] 2.2 Écrire le prompt d'extraction : JSON imposé, `null` si absent, preuve obligatoire
- [ ] 2.3 `backend/ai_agent.py` : `analyze(text)` appelle Claude et valide la réponse avec `FinancialExtraction`
- [ ] 2.4 Relance une fois avec le message d'erreur, puis exception claire
- [ ] 2.5 `backend/verify.py` : cherche chaque nombre dans le texte source (en tolérant espaces, virgules, points) et pose `verified` sur chaque `Metric`
- [ ] 2.6 `backend/tests/test_verify.py` : un faux nombre échoue, un vrai passe
- [ ] 2.7 Essai sur 3 documents réels

Fini quand : sur 3 documents réels, aucun chiffre non vérifié n'est présenté comme fiable.

### Étape 3 : API

- [ ] 3.1 `backend/main.py` : `GET /health`
- [ ] 3.2 `POST /analyze` : upload d'un PDF, renvoie le JSON vérifié
- [ ] 3.3 Erreurs propres : 400 si non-PDF, 422 si scanné, 502 si le modèle échoue après relance
- [ ] 3.4 Journal : modèle utilisé, durée, nombre de champs non vérifiés
- [ ] 3.5 Essai avec `curl` et avec la page `/docs`

Fini quand : `curl -F "file=@sample.pdf" http://localhost:8000/analyze` renvoie un JSON.

### Étape 4 : persistance (après validation de l'étape 3)

- [ ] 4.1 Installer PostgreSQL et mettre `DATABASE_URL` dans `.env`
- [ ] 4.2 Tables SQLAlchemy : `analyses` (id, filename, created_at, model, prompt_version) et `extractions` (analysis_id, payload JSON, verified_fields)
- [ ] 4.3 Constante `PROMPT_VERSION` dans `ai_agent.py`
- [ ] 4.4 Enregistrer chaque analyse faite par `POST /analyze`

Fini quand : une analyse lancée par l'API se retrouve en base.

### Étape 5 : interface React minimale (après l'étape 4)

- [ ] 5.1 Créer le projet React
- [ ] 5.2 Formulaire d'upload qui appelle `POST /analyze`
- [ ] 5.3 Affichage du JSON, champs non vérifiés en orange

Fini quand : je dépose un PDF dans le navigateur et je vois le résultat. Pas de design avant.

## Étapes avancées (après le socle)

On ne les commence qu'une fois l'étape 5 finie. Elles réutilisent toutes `verify.py` et les schémas des étapes 1 et 2.
Règle commune : un chiffre absent du texte source reste « non vérifié », quel que soit l'agent ou l'écran qui le produit.
Les noms de fichiers ci-dessous sont indicatifs, on les fixera au début de chaque étape.

### Étape 6 : agents spécialisés

Plusieurs appels à Claude, chacun avec un seul rôle, au lieu d'un seul appel qui fait tout.

- [ ] 6.1 Agent « risques » : relit le document en cherchant uniquement les risques (litiges, dépendance à un client, dette), avec preuve
- [ ] 6.2 Agent « quality of earnings » : cherche les éléments exceptionnels qui gonflent ou réduisent le résultat, avec preuve
- [ ] 6.3 Agent « contrôleur » : relit les sorties des autres agents et signale les contradictions
- [ ] 6.4 Orchestration : `analyze` lance les agents et fusionne leurs résultats dans un seul JSON validé
- [ ] 6.5 Tests : un document avec un élément exceptionnel connu doit être signalé ; `verify.py` s'applique à toutes les sorties

Fini quand : sur un document contenant un élément exceptionnel connu, l'outil le signale avec sa preuve.

### Étape 7 : plusieurs documents par dossier (data room)

- [ ] 7.1 Table `deals` : un dossier regroupe plusieurs analyses
- [ ] 7.2 Upload de plusieurs PDF dans un même dossier
- [ ] 7.3 Comparaison d'une année sur l'autre pour chaque métrique
- [ ] 7.4 Détection des contradictions : même métrique, même période, valeurs différentes selon le document
- [ ] 7.5 Tests avec deux documents fictifs qui se contredisent

Fini quand : deux documents d'un même dossier qui se contredisent déclenchent une alerte citant les deux sources.

### Étape 8 : ratios et alertes calculés en Python

Les calculs sont faits par du code, jamais par le modèle.

- [ ] 8.1 `backend/ratios.py` : marge d'EBITDA, dette nette / EBITDA, croissance du chiffre d'affaires
- [ ] 8.2 Un ratio n'est calculé que si ses deux valeurs sont vérifiées et de même unité et de même période ; sinon il vaut `null`
- [ ] 8.3 Alertes par seuils configurables (par exemple dette nette / EBITDA trop élevée)
- [ ] 8.4 Tests avec des valeurs connues, y compris division par zéro et valeurs manquantes

Fini quand : les ratios d'un document réel correspondent à un calcul fait à la main.

### Étape 9 : validation humaine

- [ ] 9.1 Chaque champ a un statut : `à valider`, `approuvé`, `corrigé`, `rejeté`
- [ ] 9.2 Routes API pour approuver, corriger ou rejeter un champ
- [ ] 9.3 Historique : qui a changé quoi, quand, et l'ancienne valeur est conservée
- [ ] 9.4 Écran de validation : la preuve s'affiche à côté de chaque champ
- [ ] 9.5 Tests : une correction ne supprime jamais la valeur extraite d'origine

Fini quand : un analyste peut corriger un chiffre et retrouver la valeur d'origine dans l'historique.

### Étape 10 : rapport exportable

- [ ] 10.1 Conserver le numéro de page de chaque preuve dès l'extraction (modifie `pdf_processor.py` et `schemas.py`)
- [ ] 10.2 Générer le rapport : métriques, ratios, risques, chacun avec sa page source
- [ ] 10.3 Les champs non vérifiés ou non approuvés sont marqués clairement dans le rapport
- [ ] 10.4 Route de téléchargement et bouton dans l'interface

Fini quand : le rapport d'un dossier se télécharge et chaque chiffre renvoie à une page du document source.

### Étape 11 : questions en langage naturel

- [ ] 11.1 Route `POST /ask` : une question sur un dossier, une réponse avec citations (passage et page)
- [ ] 11.2 Si la réponse n'est pas dans les documents, l'outil répond « non trouvé dans les documents »
- [ ] 11.3 Les nombres cités dans une réponse passent par `verify.py`
- [ ] 11.4 Champ de question dans l'interface
- [ ] 11.5 Tests : une question dont la réponse est absente ne doit pas recevoir de réponse inventée

Fini quand : une question sans réponse dans le dossier renvoie « non trouvé », et une question avec réponse renvoie sa citation.

### Étape 12 : mesure de la fiabilité

- [ ] 12.1 Jeu d'évaluation : 10 à 20 documents publics ou fictifs avec les bonnes réponses saisies à la main
- [ ] 12.2 Script d'évaluation : compare l'extraction aux bonnes réponses
- [ ] 12.3 Mesures : taux de champs exacts, taux de chiffres faux présentés comme vérifiés (objectif : zéro), taux de `null` à tort
- [ ] 12.4 Résultats enregistrés par `PROMPT_VERSION` pour comparer les versions du prompt
- [ ] 12.5 Tableau des résultats dans `README.md`

Fini quand : le README affiche des taux mesurés sur le jeu d'évaluation, reproductibles avec une seule commande.

## Où j'en suis

Prochain morceau : **0.4** (vérifier l'installation des librairies avec `pip list`).
Mets cette ligne à jour à la fin de chaque session.
