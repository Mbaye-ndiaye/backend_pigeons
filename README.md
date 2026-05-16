# 🐦 API Backend - Gestion de Volière

API REST Django pour la gestion complète d'une volière de pigeons : suivi des pigeons, couples, reproductions, sorties et cages.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)
- [Modèles de données](#-modèles-de-données)
- [Authentification](#-authentification)
- [Documentation API](#-documentation-api)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)

## ✨ Fonctionnalités

### Gestion des Pigeons
- ✅ CRUD complet des pigeons (Créer, Lire, Modifier, Supprimer)
- ✅ Suivi des informations : bague, sexe, race, date de naissance, nom
- ✅ Gestion de la généalogie (père et mère)
- ✅ Statuts : actif, vendu, mort, perdu
- ✅ Notes personnalisées

### Gestion des Couples
- ✅ Formation et dissolution de couples
- ✅ Suivi des couples actifs
- ✅ Historique des reproductions par couple
- ✅ Validation automatique (mâle + femelle)

### Gestion des Reproductions
- ✅ Enregistrement des pontes et éclosions
- ✅ Suivi du nombre de pigeonneaux
- ✅ Liaison avec les bébés nés
- ✅ Notes sur les reproductions

### Gestion des Sorties
- ✅ Enregistrement des ventes, décès et pertes
- ✅ Suivi des prix de vente
- ✅ Informations sur les acheteurs
- ✅ Mise à jour automatique du statut du pigeon

### Gestion des Cages
- ✅ Attribution de pigeons ou couples aux cages
- ✅ Libération et réaffectation des cages
- ✅ Historique des événements par cage
- ✅ Codes de cage personnalisables

### Tableau de bord
- ✅ Statistiques globales (pigeons, couples, reproductions)
- ✅ Répartition par statut, sexe et race
- ✅ Statistiques des cages occupées
- ✅ Total des ventes

## 🛠 Technologies

- **Framework** : Django 6.0.5
- **API** : Django REST Framework 3.17.1
- **Base de données** : PostgreSQL (production) / SQLite (développement)
- **Authentification** : JWT (Simple JWT 5.5.1)
- **Documentation** : drf-yasg (Swagger/OpenAPI)
- **CORS** : django-cors-headers 4.9.0
- **Soft Delete** : django-safedelete 1.4.1
- **Serveur** : Gunicorn 26.0.0 (production)

## 📦 Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 13+ (pour la production)
- pip (gestionnaire de paquets Python)
- virtualenv (recommandé)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd projet_validation
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

Créer une base de données PostgreSQL :

```sql
CREATE DATABASE voliere_db;
CREATE USER voliere_user WITH PASSWORD 'votre_mot_de_passe';
ALTER ROLE voliere_user SET client_encoding TO 'utf8';
ALTER ROLE voliere_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE voliere_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE voliere_db TO voliere_user;
```

### 5. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Django
SECRET_KEY=votre_cle_secrete_django_tres_longue_et_aleatoire
DEBUG=True

# Base de données PostgreSQL
DB_NAME=voliere_db
DB_USER=voliere_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

# Pour le déploiement (optionnel)
# DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 6. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'API sera accessible sur `http://localhost:8000/api/`

## ⚙️ Configuration

### Fichier `.env`

Le fichier `.env` contient toutes les variables d'environnement sensibles :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django | `django-insecure-xyz...` |
| `DEBUG` | Mode debug | `True` ou `False` |
| `DB_NAME` | Nom de la base de données | `voliere_db` |
| `DB_USER` | Utilisateur PostgreSQL | `voliere_user` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `password123` |
| `DB_HOST` | Hôte de la base de données | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5432` |

### CORS

Les origines autorisées sont configurées dans `backend/settings.py` :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Frontend Vite/React
    "http://127.0.0.1:5173",
]
```

## 📖 Utilisation

### Démarrer le serveur

```bash
# Mode développement
python manage.py runserver

# Mode développement avec un port spécifique
python manage.py runserver 8080

# Accessible depuis le réseau local
python manage.py runserver 0.0.0.0:8000
```

### Accéder à l'admin Django

```
URL : http://localhost:8000/admin/
Identifiants : ceux créés avec createsuperuser
```

## 🔌 API Endpoints

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register/` | Créer un compte utilisateur |
| POST | `/api/auth/login/` | Obtenir un token JWT |
| POST | `/api/auth/refresh/` | Rafraîchir le token JWT |
| GET | `/api/auth/me/` | Obtenir l'utilisateur connecté |

### Pigeons

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/pigeons/` | Liste tous les pigeons |
| POST | `/api/pigeons/` | Créer un nouveau pigeon |
| GET | `/api/pigeons/{id}/` | Détails d'un pigeon |
| PATCH | `/api/pigeons/{id}/` | Modifier un pigeon |
| DELETE | `/api/pigeons/{id}/` | Supprimer un pigeon |

### Couples

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/couples/` | Liste tous les couples |
| POST | `/api/couples/` | Former un nouveau couple |
| GET | `/api/couples/{id}/` | Détails d'un couple |
| PATCH | `/api/couples/{id}/` | Modifier un couple |
| DELETE | `/api/couples/{id}/` | Supprimer un couple |
| POST | `/api/couples/{id}/dissolve/` | Dissoudre un couple |

### Reproductions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/reproductions/` | Liste toutes les reproductions |
| POST | `/api/reproductions/` | Enregistrer une reproduction |
| GET | `/api/reproductions/{id}/` | Détails d'une reproduction |
| PATCH | `/api/reproductions/{id}/` | Modifier une reproduction |
| DELETE | `/api/reproductions/{id}/` | Supprimer une reproduction |

### Sorties

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sorties/` | Liste toutes les sorties |
| POST | `/api/sorties/` | Enregistrer une sortie |
| GET | `/api/sorties/{id}/` | Détails d'une sortie |
| PATCH | `/api/sorties/{id}/` | Modifier une sortie |
| DELETE | `/api/sorties/{id}/` | Supprimer une sortie |

### Cages

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/cages/` | Liste toutes les cages |
| POST | `/api/cages/` | Créer une nouvelle cage |
| GET | `/api/cages/{id}/` | Détails d'une cage |
| PATCH | `/api/cages/{id}/` | Modifier une cage |
| DELETE | `/api/cages/{id}/` | Supprimer une cage |
| POST | `/api/cages/{id}/assign/` | Affecter un pigeon/couple |
| POST | `/api/cages/{id}/free/` | Libérer une cage |
| GET | `/api/cages/{id}/history/` | Historique d'une cage |
| POST | `/api/cages/{id}/history/` | Ajouter un événement |

### Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/dashboard/stats/` | Statistiques globales |

## 📊 Modèles de données

### Pigeon

```python
{
    "id": 1,
    "bague": "P001",
    "nom": "Champion",
    "sex": "M",  # M ou F
    "race": "Voyageur",
    "birth_date": "2024-01-15",
    "parent_male": 5,  # ID du père
    "parent_female": 6,  # ID de la mère
    "status": "actif",  # actif, vendu, mort, perdu
    "notes": "Excellent reproducteur",
    "created_at": "2024-01-01T10:00:00Z"
}
```

### Couple

```python
{
    "id": 1,
    "male": {
        "id": 1,
        "bague": "P001",
        "race": "Voyageur",
        ...
    },
    "female": {
        "id": 2,
        "bague": "P002",
        "race": "Voyageur",
        ...
    },
    "formed_at": "2024-01-01",
    "active": true,
    "dissolved_at": null
}
```

### Reproduction

```python
{
    "id": 1,
    "couple": 1,
    "pond_date": "2024-02-01",
    "hatch_date": "2024-02-18",
    "count": 2,
    "babies": [10, 11],  # IDs des pigeonneaux
    "notes": "Éclosion réussie"
}
```

### Sortie

```python
{
    "id": 1,
    "pigeon": 5,
    "pigeon_bague": "P005",
    "type": "vente",  # vente, deces, perte
    "date": "2024-03-01",
    "buyer": "Jean Dupont",
    "price": "150.00",
    "reason": "Bon reproducteur"
}
```

### Cage

```python
{
    "id": 1,
    "code": "A16",
    "pigeon": {
        "id": 1,
        "bague": "P001",
        ...
    },
    "couple": null
}
```

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### Obtenir un token

```bash
POST /api/auth/login/
Content-Type: application/json

{
    "username": "votre_username",
    "password": "votre_password"
}
```

Réponse :

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Utiliser le token

Ajouter le header `Authorization` à chaque requête :

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Rafraîchir le token

```bash
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 📚 Documentation API

### Swagger UI

Documentation interactive disponible sur :

```
http://localhost:8000/api/swagger/
```

### ReDoc

Documentation alternative sur :

```
http://localhost:8000/api/redoc/
```

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
python manage.py test

# Tests d'une application spécifique
python manage.py test api

# Tests avec verbosité
python manage.py test --verbosity=2

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
```

### Créer des tests

Les tests sont dans `api/tests.py` :

```python
from django.test import TestCase
from api.models import Pigeon

class PigeonTestCase(TestCase):
    def setUp(self):
        Pigeon.objects.create(
            bague="TEST001",
            sex="M",
            race="Test Race"
        )

    def test_pigeon_creation(self):
        pigeon = Pigeon.objects.get(bague="TEST001")
        self.assertEqual(pigeon.sex, "M")
```

## 🚢 Déploiement

### Préparation

1. **Désactiver le mode DEBUG**

```python
# backend/settings.py
DEBUG = False
```

2. **Configurer ALLOWED_HOSTS**

```python
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']
```

3. **Collecter les fichiers statiques**

```bash
python manage.py collectstatic
```

### Avec Gunicorn

```bash
# Installer Gunicorn (déjà dans requirements.txt)
pip install gunicorn

# Lancer le serveur
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

### Variables d'environnement en production

```env
SECRET_KEY=votre_cle_secrete_production
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/dbname
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

### Avec Docker (optionnel)

Créer un `Dockerfile` :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🤝 Contribution

### Structure du projet

```
projet_validation/
├── api/                    # Application principale
│   ├── migrations/         # Migrations de base de données
│   ├── models.py          # Modèles de données
│   ├── serializers.py     # Sérialiseurs DRF
│   ├── views.py           # Vues et ViewSets
│   ├── urls.py            # Routes de l'API
│   └── admin.py           # Configuration admin Django
├── backend/               # Configuration Django
│   ├── settings.py        # Paramètres du projet
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Point d'entrée WSGI
├── manage.py              # Script de gestion Django
├── requirements.txt       # Dépendances Python
├── .env                   # Variables d'environnement (à créer)
└── README.md             # Ce fichier
```

### Workflow de développement

1. Créer une branche pour votre fonctionnalité
2. Faire vos modifications
3. Écrire des tests
4. Vérifier que tous les tests passent
5. Créer une pull request

### Standards de code

- Suivre PEP 8 pour le style Python
- Documenter les fonctions et classes
- Écrire des tests pour les nouvelles fonctionnalités
- Utiliser des noms de variables explicites

## 📝 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- **Votre Nom** - Développeur principal

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter : votre.email@example.com

## 🔄 Changelog

### Version 1.0.0 (2024)
- ✅ Gestion complète des pigeons
- ✅ Gestion des couples et reproductions
- ✅ Gestion des sorties (ventes, décès, pertes)
- ✅ Gestion des cages avec historique
- ✅ Authentification JWT
- ✅ Documentation Swagger/OpenAPI
- ✅ Tableau de bord avec statistiques

---

**Note** : Ce README est un document vivant. N'hésitez pas à le mettre à jour au fur et à mesure de l'évolution du projet.
