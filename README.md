# HealthTime

<img src="./HealthTime/assets/logo_light.png" alt="HealthTime Logo" width="180"/>

**HealthTime** est une plateforme de gestion de services médicaux intégrée.  
Elle propose une architecture hybride permettant :

- Aux **patients** de réserver en ligne via une interface **Web**
- Aux **professionnels de santé** de gérer leur activité via une application **Desktop (GUI)**
- Le tout synchronisé sur une base de données **PostgreSQL** unique

---

## Fonctionnalités principales

### Double Interface

- Application **Desktop** développée avec **Tkinter**
- Portail **Web** développé avec **Flask**

### Gestion des Profils

- Tableaux de bord spécifiques pour :
  - Patients
  - Docteurs
  - Administrateurs

### Thèmes Dynamiques

- Mode **Clair**
- Mode **Sombre**
- Ressources graphiques dédiées (`logo_dark.png`, `logo_light.png`)

### Fiabilité

- Tests unitaires pour :
  - Couche DAO
  - Base de données

### Persistance

- Modèle relationnel robuste sous **PostgreSQL**

---

## Déploiement en Production

L'application **HealthTime** est déployée en ligne via la plateforme **Render**.

### Hébergement

- Application Web : https://healthtime-a2vr.onrender.com/
- Base de données : PostgreSQL hébergée sur Render
- Variables d'environnement configurées via le dashboard Render

L’application utilise une base PostgreSQL distante en production, distincte de l’environnement local.

## Configuration des Variables d’Environnement

Le projet utilise un fichier `.env` pour sécuriser les informations sensibles.

### Exemple de fichier `.env` (en local)

```env
# Database Connection
DB_NAME=healthtime
DB_USER=postgres
DB_PASSWORD=YourPassword
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=YourSuperSecretKey
```

## Installation et Configuration

### Prérequis

- Python **3.10+**
- PostgreSQL

---

### Installation des dépendances

Le projet utilise un fichier de dépendances situé dans le répertoire `web` :

```bash
pip install -r web/requirements.txt
```

## Base de données

1. Créez une base de données PostgreSQL
2. Initialisez les tables avec :

```bash
database/schema.sql
```

3. Configurez vos accès dans :
   - `config/settings.py`
   - `database/db.py`

## Lancement du Projet

### 1. Application Desktop (GUI)

Pour l'administration et le suivi médical :
`python main.py`

### 2. Portail Web

Pour la prise de rendez-vous en ligne : `python web/app.py`

## Organisation du Code

```bash
HealthTime/
├── main.py                 # Point d'entrée de l'application Desktop
├── assets/                 # Ressources graphiques
│   ├── logo_dark.png       # Logo pour le thème sombre
│   └── logo_light.png      # Logo pour le thème clair
├── config/                 # Paramètres de l'application
│   └── settings.py         # Configuration globale (DB, thèmes, etc.)
├── dao/                    # Couche d'accès aux données (Patterns DAO)
│   ├── admin_dao.py
│   ├── appointment_dao.py
│   ├── doctor_dao.py
│   └── user_dao.py
├── database/               # Gestion de la persistance
│   ├── db.py               # Singleton de connexion PostgreSQL
│   └── schema.sql          # Script de création des tables
├── gui/                    # Interface graphique Tkinter
│   ├── dashboards/         # Tableaux de bord spécifiques par rôle
│   │   ├── admin_dashboard.py
│   │   ├── doctor_dashboard.py
│   │   └── patient_dashboard.py
│   ├── login_view.py       # Fenêtre de connexion
│   └── register_view.py    # Fenêtre d'inscription
├── tests/                  # Tests unitaires et d'intégration
│   ├── test_admin_dao.py
│   ├── test_db.py
│   └── test_user_dao.py
└── web/                    # Architecture de la plateforme Web Flask
    ├── app.py              # Routes et logique du serveur Web
    ├── init_db.py          # Script d'initialisation spécifique au Web
    ├── requirements.txt    # Liste des dépendances Python
    ├── static/             # Fichiers statiques
    │   └── style.css       # Feuilles de style CSS pour le portail
    └── templates/          # Vues HTML (Moteur Jinja2)
        ├── admin/          # dashboard.html (Admin)
        |   └── dashboard.html
        ├── doctor/         # dashboard.html (Doctor)
        |   └── dashboard.html
        ├── patient/        # dashboard.html (Patient)
        |   └── dashboard.html
        ├── base.html       # Squelette HTML commun
        ├── home.html       # Page d'accueil du portail
        ├── login.html      # Formulaire de connexion web
        ├── register.html   # Formulaire d'inscription web
        └── search.html     # Moteur de recherche de praticiens
```

---

## ⚖️ Licence

Projet réalisé dans un cadre académique.

---

© 2026 HealthTime — Tous droits réservés. - Développé par Asma
