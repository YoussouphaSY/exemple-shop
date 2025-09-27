# Shop360 - Système de Gestion de Boutique

Shop360 est une application web complète de gestion de boutique développée avec Django. Elle offre une vue 360° sur votre business : stocks, ventes, achats, finances et analytics.

## 🚀 Fonctionnalités

### Gestion des Produits
- CRUD complet des produits avec catégories
- Gestion des images produits
- Suivi des prix d'achat et de vente
- Calcul automatique des marges

### Gestion du Stock
- Suivi en temps réel des quantités
- Alertes de stock critique
- Mouvements de stock automatiques
- Système d'inventaire

### Ventes
- Interface de caisse moderne
- Gestion des clients
- Tickets de vente imprimables
- Statistiques de vente

### Achats
- Gestion des fournisseurs
- Suivi des commandes
- Réception et facturation
- Mise à jour automatique des stocks

### Finance
- Suivi des recettes et dépenses
- Tableau de bord financier
- Gestion de la caisse
- Rapports financiers
- Export Excel/CSV

### Dashboard & Analytics
- Vue d'ensemble temps réel
- Graphiques interactifs (Chart.js)
- Top produits
- Évolution des ventes
- Indicateurs clés de performance

### API REST
- API complète avec Django REST Framework
- Authentification par token
- Endpoints pour toutes les entités
- Pagination et filtres

### Système d'Utilisateurs
- Rôles et permissions (Admin, Gestionnaire, Caissier)
- Gestion des profils
- Authentification sécurisée

## 🛠️ Technologies

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Bootstrap 5, Chart.js
- **Base de données**: SQLite (configurable MySQL)
- **Authentification**: Django Auth + Token Auth
- **Exports**: openpyxl, reportlab
- **Formulaires**: django-crispy-forms

## 📦 Installation

### Prérequis
- Python 3.11+
- pip
- virtualenv (recommandé)

### Installation locale

1. **Cloner le projet**
```bash
git clone <repository-url>
cd shop360
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
cp .env.example .env
# Modifier le fichier .env avec vos paramètres
```

5. **Migrations et données d'exemple**
```bash
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur**
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : http://127.0.0.1:8000

### Données de test

Les fixtures incluent :
- **Utilisateur admin** : `admin` / `Admin123!`
- **10 produits** d'exemple (téléphones, accessoires, tablettes)
- **3 fournisseurs** fictifs
- **Catégories** prédéfinies

## 🎯 Utilisation

### Rôles et Permissions

#### Administrateur
- Accès complet à toutes les fonctionnalités
- Gestion des utilisateurs
- Configuration système

#### Gestionnaire
- Gestion des produits, stocks, achats
- Accès aux rapports financiers
- Gestion des inventaires

#### Caissier
- Interface de vente
- Consultation des stocks
- Transactions basiques

### Interface Principale

1. **Dashboard** : Vue d'ensemble avec KPI et graphiques
2. **Produits** : Catalogue avec recherche et filtres
3. **Ventes** : Interface de caisse et historique
4. **Achats** : Commandes fournisseurs et réceptions
5. **Stock** : Mouvements et inventaires
6. **Finance** : Suivi comptable et rapports

### API REST

Base URL : `/api/`

Endpoints principaux :
- `GET /api/produits/` - Liste des produits
- `POST /api/ventes/` - Créer une vente
- `GET /api/dashboard/stats/` - Statistiques dashboard
- `GET /api/stock/mouvements/` - Mouvements de stock

Authentification :
```bash
# Obtenir un token
POST /api-token-auth/
{
    "username": "your_username",
    "password": "your_password"
}

# Utiliser le token
Authorization: Token your-token-here
```

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Rapport HTML dans htmlcov/
```

## 📊 Structure du Projet

```
shop360/
├── manage.py
├── shop360/                    # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                       # Applications Django
│   ├── users/                  # Gestion utilisateurs
│   ├── produits/              # Gestion produits
│   ├── stock/                 # Gestion stock
│   ├── ventes/                # Gestion ventes
│   ├── achats/                # Gestion achats
│   ├── finance/               # Gestion financière
│   └── dashboard/             # Tableau de bord
├── templates/                  # Templates HTML
│   ├── base.html
│   ├── dashboard/
│   ├── produits/
│   └── ...
├── static/                     # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
├── fixtures/                   # Données d'exemple
└── requirements.txt
```


---

- Solde total : c’est le solde global après avoir pris en compte recettes, dépenses et budgets actifs.

- Solde en caisse : c’est la caisse physique actuelle, qui n’intègre pas les budgets prévisionnels.

**Shop360** - Une solution complète pour la gestion de votre boutique ! 🏪✨