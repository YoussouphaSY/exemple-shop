# 📚 Shop360 - Documentation Technique Détaillée

> **Application de Gestion Complète pour Boutiques**  
> Système intégré de gestion des ventes, stocks, achats, finances et utilisateurs

---

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture du Projet](#architecture-du-projet)
3. [Applications Django](#applications-django)
   - [Users (Utilisateurs)](#1-users---gestion-des-utilisateurs)
   - [Produits](#2-produits---catalogue-produits)
   - [Stock](#3-stock---gestion-des-stocks)
   - [Ventes](#4-ventes---point-de-vente)
   - [Achats](#5-achats---approvisionnement)
   - [Finance](#6-finance---comptabilité)
   - [Dashboard](#7-dashboard---tableau-de-bord)
4. [Système de Permissions](#système-de-permissions)
5. [API REST](#api-rest)
6. [Templates et Frontend](#templates-et-frontend)
7. [Fonctionnalités Avancées](#fonctionnalités-avancées)

---

## Vue d'Ensemble

**Shop360** est une application web Django complète pour la gestion d'une boutique. Elle couvre tous les aspects de la gestion commerciale :

- 👥 **Gestion multi-utilisateurs** avec rôles (Admin, Manager, Caissier)
- 📦 **Catalogue produits** avec catégories et images
- 📊 **Suivi des stocks** en temps réel avec alertes
- 💰 **Point de vente (POS)** moderne et intuitif
- 🛒 **Gestion des achats** fournisseurs
- 💳 **Comptabilité** et gestion de trésorerie
- 📈 **Tableaux de bord** et analytics

---

## Architecture du Projet

### Structure des Dossiers

\`\`\`
project/
├── shop360/                    # Configuration principale Django
│   ├── settings.py            # Paramètres de l'application
│   ├── urls.py                # Routage principal
│   └── wsgi.py                # Point d'entrée WSGI
│
├── apps/                       # Applications Django modulaires
│   ├── users/                 # Gestion des utilisateurs
│   ├── produits/              # Catalogue produits
│   ├── stock/                 # Gestion des stocks
│   ├── ventes/                # Point de vente
│   ├── achats/                # Approvisionnement
│   ├── finance/               # Comptabilité
│   └── dashboard/             # Tableau de bord
│
├── templates/                  # Templates HTML
│   ├── base.html              # Template de base
│   ├── users/                 # Templates utilisateurs
│   ├── produits/              # Templates produits
│   ├── stock/                 # Templates stock
│   ├── ventes/                # Templates ventes
│   ├── achats/                # Templates achats
│   ├── finance/               # Templates finance
│   └── dashboard/             # Templates dashboard
│
├── static/                     # Fichiers statiques
│   ├── css/                   # Feuilles de style
│   ├── js/                    # Scripts JavaScript
│   └── images/                # Images
│
├── media/                      # Fichiers uploadés
│   └── produits/              # Images produits
│
└── manage.py                   # Script de gestion Django
\`\`\`

### Technologies Utilisées

- **Backend** : Django 5.1.5, Python 3.11+
- **API** : Django REST Framework
- **Base de données** : SQLite (dev), MySQL/PostgreSQL (prod)
- **Frontend** : Bootstrap 5, Chart.js, JavaScript vanilla
- **Formulaires** : Django Crispy Forms
- **Export** : openpyxl (Excel), ReportLab (PDF)

---

## Applications Django

## 1. Users - Gestion des Utilisateurs

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Modèles User, UserSession, DailyAttendance | 122 |
| \`views.py\` | Vues d'inscription, profil, liste utilisateurs | 97 |
| \`forms.py\` | Formulaires d'inscription et mise à jour | 78 |
| \`decorators.py\` | Décorateurs de permissions personnalisés | 39 |
| \`middleware.py\` | Middleware de suivi des sessions | 32 |
| \`signals.py\` | Signaux pour création de sessions | 80 |
| \`admin.py\` | Interface d'administration | 70 |

### 🎯 Fonctionnalités

#### Modèle User Personnalisé
\`\`\`python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Choix: 'admin', 'manager', 'cashier'
\`\`\`

**Rôles et Permissions** :
- **Admin** : Accès complet, gestion utilisateurs, configuration
- **Manager** : Gestion produits, stocks, ventes, achats, rapports
- **Cashier** : Accès caisse, ventes uniquement

#### Suivi des Sessions
\`\`\`python
class UserSession(models.Model):
    user = models.ForeignKey(User)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
\`\`\`

Permet de tracker :
- Heures de connexion/déconnexion
- Sessions actives
- Présence quotidienne

#### Décorateurs de Permissions

**Fichier : \`decorators.py\`**

\`\`\`python
@admin_required
def admin_only_view(request):
    # Accessible uniquement aux admins
    pass

@manager_or_admin_cashier_required
def manager_view(request):
    # Accessible aux managers, admins et caissiers
    pass

@cashier_access
def cashier_view(request):
    # Accessible à tous les rôles
    pass
\`\`\`

#### Middleware de Session

**Fichier : \`middleware.py\`**

Suit automatiquement l'activité des utilisateurs connectés et met à jour leurs sessions.

### 🔗 URLs Disponibles

| URL | Vue | Permission | Description |
|-----|-----|------------|-------------|
| \`/users/register/\` | RegisterView | Admin | Créer un utilisateur |
| \`/users/profile/\` | ProfileView | Connecté | Modifier son profil |
| \`/users/\` | UserListView | Admin/Manager | Liste utilisateurs |
| \`/users/<id>/\` | UserDetailView | Admin/Manager | Détails utilisateur |
| \`/users/<id>/edit/\` | UserUpdateView | Admin | Modifier utilisateur |

---

## 2. Produits - Catalogue Produits

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Modèles Categorie et Produit | 94 |
| \`views.py\` | CRUD produits et catégories | 140 |
| \`forms.py\` | Formulaires produits | 95 |
| \`serializers.py\` | Sérialiseurs API REST | 19 |
| \`api_views.py\` | ViewSets API | 40 |
| \`templatetags/\` | Filtres personnalisés | - |

### 🎯 Fonctionnalités

#### Modèle Produit
\`\`\`python
class Produit(models.Model):
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    categorie = models.ForeignKey(Categorie)
    description = models.TextField(blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=10)
    image = models.ImageField(upload_to='produits/', blank=True)
    actif = models.BooleanField(default=True)
\`\`\`

#### Propriétés Calculées
\`\`\`python
@property
def benefice_unitaire(self):
    return self.prix_vente - self.prix_achat

@property
def marge_pourcentage(self):
    if self.prix_achat > 0:
        return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100
    return 0

@property
def stock_critique(self):
    return self.quantite_stock <= self.seuil_alerte
\`\`\`

#### Méthodes Utiles
\`\`\`python
def update_stock(self, quantite, operation='add'):
    \"\"\"Met à jour le stock (add ou subtract)\"\"\"
    if operation == 'add':
        self.quantite_stock += quantite
    elif operation == 'subtract':
        if self.quantite_stock >= quantite:
            self.quantite_stock -= quantite
        else:
            raise ValueError("Stock insuffisant")
    self.save()
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Permission | Description |
|-----|-----|------------|-------------|
| \`/produits/\` | ProduitListView | Tous | Liste produits |
| \`/produits/create/\` | ProduitCreateView | Admin/Manager | Créer produit |
| \`/produits/<id>/\` | ProduitDetailView | Tous | Détails produit |
| \`/produits/<id>/edit/\` | ProduitUpdateView | Admin/Manager | Modifier produit |
| \`/produits/<id>/delete/\` | ProduitDeleteView | Admin | Supprimer produit |
| \`/produits/quick-create/\` | ProduitQuickCreateView | Admin/Manager | Création rapide (AJAX) |

### 🌐 API REST

**Endpoints** :
- \`GET /api/produits/\` - Liste produits
- \`POST /api/produits/\` - Créer produit
- \`GET /api/produits/{id}/\` - Détails produit
- \`PUT /api/produits/{id}/\` - Modifier produit
- \`DELETE /api/produits/{id}/\` - Supprimer produit

**Sérialiseur** :
\`\`\`python
class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    stock_critique = serializers.BooleanField(read_only=True)
    benefice_unitaire = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    marge_pourcentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
\`\`\`

---

## 3. Stock - Gestion des Stocks

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | MouvementStock, Inventaire, InventaireItem | 145 |
| \`views.py\` | Mouvements, inventaires, alertes | 230 |
| \`forms.py\` | Formulaires stock | 60 |

### 🎯 Fonctionnalités

#### Mouvements de Stock
\`\`\`python
class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('inventaire', 'Inventaire'),
    ]
    
    produit = models.ForeignKey(Produit)
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    source = models.CharField(max_length=100)  # Ex: "Vente #123", "Achat #45"
    utilisateur = models.ForeignKey(User)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    remarque = models.TextField(blank=True)
\`\`\`

**Méthode de Création** :
\`\`\`python
@classmethod
def create_mouvement(cls, produit, type_mouvement, quantite, source, utilisateur, remarque=''):
    \"\"\"Crée un mouvement et met à jour le stock automatiquement\"\"\"
    mouvement = cls.objects.create(
        produit=produit,
        type_mouvement=type_mouvement,
        quantite=quantite,
        source=source,
        utilisateur=utilisateur,
        remarque=remarque
    )
    
    # Mise à jour automatique du stock
    if type_mouvement in ['entree', 'ajustement']:
        produit.update_stock(quantite, 'add')
    elif type_mouvement == 'sortie':
        produit.update_stock(quantite, 'subtract')
    
    return mouvement
\`\`\`

#### Inventaires Physiques
\`\`\`python
class Inventaire(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    date_inventaire = models.DateField()
    statut = models.CharField(max_length=20, choices=[
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('valide', 'Validé')
    ])
    utilisateur = models.ForeignKey(User)
    remarques = models.TextField(blank=True)

class InventaireItem(models.Model):
    inventaire = models.ForeignKey(Inventaire, related_name='items')
    produit = models.ForeignKey(Produit)
    quantite_systeme = models.IntegerField()  # Stock dans le système
    quantite_comptee = models.IntegerField()  # Stock compté physiquement
    
    @property
    def ecart(self):
        return self.quantite_comptee - self.quantite_systeme
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| \`/stock/\` | StockListView | Liste des stocks |
| \`/stock/mouvements/\` | MouvementListView | Historique mouvements |
| \`/stock/mouvements/create/\` | MouvementCreateView | Créer mouvement |
| \`/stock/inventaires/\` | InventaireListView | Liste inventaires |
| \`/stock/inventaires/create/\` | InventaireCreateView | Nouvel inventaire |
| \`/stock/inventaires/<id>/\` | InventaireDetailView | Détails inventaire |
| \`/stock/alertes/\` | AlertesStockView | Produits en alerte |

---

## 4. Ventes - Point de Vente

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Vente, VenteItem | 162 |
| \`views.py\` | Caisse, ventes, exports | 248 |
| \`forms.py\` | Formulaires ventes | 55 |
| \`templates/ventes/caisse.html\` | Interface POS | 669 |

### 🎯 Fonctionnalités

#### Modèle Vente
\`\`\`python
class Vente(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    client = models.CharField(max_length=200, blank=True)
    telephone_client = models.CharField(max_length=20, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mode_paiement = models.CharField(max_length=20, choices=[
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('mobile', 'Mobile Money')
    ])
    vendeur = models.ForeignKey(User, related_name='ventes_vendeur')
    finalisee = models.BooleanField(default=False)
\`\`\`

#### Modèle VenteItem (avec Prix Négociable) ⭐ NOUVEAU
\`\`\`python
class VenteItem(models.Model):
    vente = models.ForeignKey(Vente, related_name='items')
    produit = models.ForeignKey(Produit)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    prix_original = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # NOUVEAU
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def reduction_accordee(self):
        \"\"\"Calcule la réduction accordée\"\"\"
        if self.prix_original and self.prix_original > self.prix_unitaire:
            return self.prix_original - self.prix_unitaire
        return 0
    
    @property
    def pourcentage_reduction(self):
        \"\"\"Calcule le pourcentage de réduction\"\"\"
        if self.prix_original and self.prix_original > 0:
            return ((self.prix_original - self.prix_unitaire) / self.prix_original) * 100
        return 0
\`\`\`

#### Finalisation de Vente
\`\`\`python
def finaliser(self):
    \"\"\"Finalise la vente : met à jour stock et crée transaction financière\"\"\"
    if self.finalisee:
        raise ValidationError("Cette vente est déjà finalisée")
    
    # Mise à jour des stocks
    for item in self.items.all():
        MouvementStock.create_mouvement(
            produit=item.produit,
            type_mouvement='sortie',
            quantite=item.quantite,
            source=f'Vente {self.numero}',
            utilisateur=self.vendeur
        )
    
    # Création de la transaction financière
    Transaction.objects.create(
        type_transaction='revenu',
        categorie='vente',
        montant=self.total_ttc,
        description=f'Vente {self.numero}',
        vente=self,
        utilisateur=self.vendeur
    )
    
    self.finalisee = True
    self.save()
\`\`\`

#### Interface de Caisse (POS)

**Fichier : \`templates/ventes/caisse.html\`**

Fonctionnalités JavaScript :
- ✅ Recherche et filtrage produits en temps réel
- ✅ Ajout au panier avec gestion du stock
- ✅ **Modification du prix unitaire (négociation)** ⭐ NOUVEAU
- ✅ **Affichage des réductions accordées** ⭐ NOUVEAU
- ✅ Calcul automatique des totaux
- ✅ Validation avant finalisation
- ✅ Impression du ticket de caisse
- ✅ Création rapide de produits

**Exemple de négociation de prix** :
\`\`\`javascript
// Le caissier peut modifier le prix dans le panier
function updatePrice(index, newPrice) {
    const item = cart[index];
    const price = parseFloat(newPrice);
    
    // Alerte si réduction > 50%
    if (price < item.originalPrice * 0.5) {
        if (!confirm(\`Réduction de \${reduction}% - Confirmer?\`)) {
            return;
        }
    }
    
    item.price = price;
    updateCartDisplay();  // Affiche la réduction en temps réel
}
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| \`/ventes/\` | VenteListView | Liste des ventes |
| \`/ventes/caisse/\` | CaisseView | Interface POS |
| \`/ventes/create/\` | VenteCreateView | Créer vente (formulaire) |
| \`/ventes/<id>/\` | VenteDetailView | Détails vente |
| \`/ventes/<id>/ticket/\` | TicketView | Ticket de caisse |
| \`/ventes/<id>/finaliser/\` | FinalizeVenteView | Finaliser vente |
| \`/ventes/export/\` | ExportVentesView | Export CSV/Excel |

---

## 5. Achats - Approvisionnement

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Fournisseur, Achat, AchatItem | 150 |
| \`views.py\` | CRUD achats et fournisseurs | 252 |
| \`forms.py\` | Formulaires achats | 110 |

### 🎯 Fonctionnalités

#### Modèle Fournisseur
\`\`\`python
class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    actif = models.BooleanField(default=True)
\`\`\`

#### Modèle Achat
\`\`\`python
class Achat(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('commande', 'Commandé'),
        ('recu', 'Reçu'),
        ('facture', 'Facturé'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    fournisseur = models.ForeignKey(Fournisseur)
    date_commande = models.DateField()
    date_reception = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utilisateur = models.ForeignKey(User)
\`\`\`

#### Réception d'Achat
\`\`\`python
def recevoir(self):
    \"\"\"Marque l'achat comme reçu et met à jour les stocks\"\"\"
    if self.statut != 'commande':
        raise ValidationError("Seuls les achats commandés peuvent être reçus")
    
    # Mise à jour des stocks
    for item in self.items.all():
        MouvementStock.create_mouvement(
            produit=item.produit,
            type_mouvement='entree',
            quantite=item.quantite,
            source=f'Achat {self.numero}',
            utilisateur=self.utilisateur,
            remarque=f'Réception fournisseur {self.fournisseur.nom}'
        )
    
    self.statut = 'recu'
    self.date_reception = timezone.now().date()
    self.save()
\`\`\`

#### Facturation d'Achat
\`\`\`python
def facturer(self):
    \"\"\"Marque l'achat comme facturé et crée la transaction financière\"\"\"
    if self.statut != 'recu':
        raise ValidationError("L'achat doit être reçu avant d'être facturé")
    
    # Création de la transaction financière
    Transaction.objects.create(
        type_transaction='depense',
        categorie='achat',
        montant=self.total_ttc,
        description=f'Achat {self.numero} - {self.fournisseur.nom}',
        achat=self,
        utilisateur=self.utilisateur
    )
    
    self.statut = 'facture'
    self.save()
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| \`/achats/\` | AchatListView | Liste des achats |
| \`/achats/create/\` | AchatCreateView | Créer achat |
| \`/achats/<id>/\` | AchatDetailView | Détails achat |
| \`/achats/<id>/edit/\` | AchatUpdateView | Modifier achat |
| \`/achats/<id>/recevoir/\` | RecevoirAchatView | Réceptionner achat |
| \`/achats/<id>/facturer/\` | FacturerAchatView | Facturer achat |
| \`/achats/fournisseurs/\` | FournisseurListView | Liste fournisseurs |
| \`/achats/fournisseurs/create/\` | FournisseurCreateView | Créer fournisseur |

---

## 6. Finance - Comptabilité

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Transaction, Budget, CaisseFonds | 317 |
| \`views.py\` | Transactions, budgets, caisse | 468 |
| \`forms.py\` | Formulaires finance | 145 |

### 🎯 Fonctionnalités

#### Modèle Transaction
\`\`\`python
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('revenu', 'Revenu'),
        ('depense', 'Dépense'),
    ]
    
    CATEGORIE_CHOICES = [
        ('vente', 'Vente'),
        ('achat', 'Achat'),
        ('salaire', 'Salaire'),
        ('loyer', 'Loyer'),
        ('electricite', 'Électricité'),
        ('eau', 'Eau'),
        ('internet', 'Internet'),
        ('autre', 'Autre'),
    ]
    
    type_transaction = models.CharField(max_length=20, choices=TYPE_CHOICES)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date_transaction = models.DateTimeField(auto_now_add=True)
    vente = models.ForeignKey(Vente, null=True, blank=True)
    achat = models.ForeignKey(Achat, null=True, blank=True)
    utilisateur = models.ForeignKey(User)
\`\`\`

**Calcul du Solde** :
\`\`\`python
@classmethod
def get_solde(cls, date_debut=None, date_fin=None):
    \"\"\"Calcule le solde sur une période\"\"\"
    transactions = cls.objects.all()
    
    if date_debut:
        transactions = transactions.filter(date_transaction__gte=date_debut)
    if date_fin:
        transactions = transactions.filter(date_transaction__lte=date_fin)
    
    revenus = transactions.filter(type_transaction='revenu').aggregate(
        total=Sum('montant'))['total'] or 0
    depenses = transactions.filter(type_transaction='depense').aggregate(
        total=Sum('montant'))['total'] or 0
    
    return revenus - depenses
\`\`\`

#### Modèle Budget
\`\`\`python
class Budget(models.Model):
    categorie = models.CharField(max_length=50)
    montant_prevu = models.DecimalField(max_digits=10, decimal_places=2)
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    utilisateur = models.ForeignKey(User)
    
    @property
    def montant_depense(self):
        \"\"\"Calcule le montant dépensé sur la période\"\"\"
        return Transaction.objects.filter(
            type_transaction='depense',
            categorie=self.categorie,
            date_transaction__gte=self.periode_debut,
            date_transaction__lte=self.periode_fin
        ).aggregate(total=Sum('montant'))['total'] or 0
    
    @property
    def montant_restant(self):
        return self.montant_prevu - self.montant_depense
    
    @property
    def pourcentage_utilise(self):
        if self.montant_prevu > 0:
            return (self.montant_depense / self.montant_prevu) * 100
        return 0
\`\`\`

#### Modèle CaisseFonds
\`\`\`python
class CaisseFonds(models.Model):
    TYPE_CHOICES = [
        ('ouverture', 'Ouverture de caisse'),
        ('fermeture', 'Fermeture de caisse'),
        ('approvisionnement', 'Approvisionnement'),
        ('retrait', 'Retrait'),
    ]
    
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(User)
    remarque = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Créer une transaction pour les retraits et fermetures
        if self.type_mouvement in ['retrait', 'fermeture']:
            Transaction.objects.create(
                type_transaction='depense',
                categorie='autre',
                montant=self.montant,
                description=f'{self.get_type_mouvement_display()} - {self.remarque}',
                utilisateur=self.utilisateur
            )
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| \`/finance/\` | FinanceOverviewView | Vue d'ensemble |
| \`/finance/transactions/\` | TransactionListView | Liste transactions |
| \`/finance/transactions/create/\` | TransactionCreateView | Créer transaction |
| \`/finance/budgets/\` | BudgetListView | Liste budgets |
| \`/finance/budgets/create/\` | BudgetCreateView | Créer budget |
| \`/finance/caisse/\` | CaisseView | Gestion caisse |
| \`/finance/rapports/\` | RapportsView | Rapports financiers |

---

## 7. Dashboard - Tableau de Bord

### 📁 Fichiers Principaux

| Fichier | Rôle | Lignes |
|---------|------|--------|
| \`models.py\` | Notification, ParametreSysteme | 47 |
| \`views.py\` | Dashboard, analytics, charts | 310 |
| \`admin.py\` | Interface admin avancée | 310 |

### 🎯 Fonctionnalités

#### Vue Dashboard Principale
\`\`\`python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # KPIs du jour
        context['ventes_aujourd_hui'] = Vente.objects.filter(
            date_vente__date=today, finalisee=True
        ).count()
        
        context['ca_aujourd_hui'] = Vente.objects.filter(
            date_vente__date=today, finalisee=True
        ).aggregate(total=Sum('total_ttc'))['total'] or 0
        
        # Produits en alerte
        context['produits_alerte'] = Produit.objects.filter(
            quantite_stock__lte=F('seuil_alerte')
        ).count()
        
        # Top 5 produits vendus
        context['top_produits'] = VenteItem.objects.values(
            'produit__nom'
        ).annotate(
            total_vendu=Sum('quantite')
        ).order_by('-total_vendu')[:5]
        
        # Graphiques
        context['chart_data'] = self.get_chart_data()
        
        return context
\`\`\`

#### API de Données pour Graphiques
\`\`\`python
class ChartDataView(LoginRequiredMixin, View):
    def get(self, request):
        chart_type = request.GET.get('type', 'sales')
        
        if chart_type == 'sales':
            data = self.get_sales_chart_data()
        elif chart_type == 'products':
            data = self.get_products_chart_data()
        elif chart_type == 'categories':
            data = self.get_categories_chart_data()
        
        return JsonResponse(data)
    
    def get_sales_chart_data(self):
        \"\"\"Données de ventes sur les 7 derniers jours\"\"\"
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        sales_by_day = Vente.objects.filter(
            date_vente__date__gte=start_date,
            date_vente__date__lte=end_date,
            finalisee=True
        ).values('date_vente__date').annotate(
            total=Sum('total_ttc'),
            count=Count('id')
        ).order_by('date_vente__date')
        
        return {
            'labels': [s['date_vente__date'].strftime('%d/%m') for s in sales_by_day],
            'data': [float(s['total']) for s in sales_by_day]
        }
\`\`\`

#### Modèle Notification
\`\`\`python
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('success', 'Succès'),
    ]
    
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    lue = models.BooleanField(default=False)
    utilisateur = models.ForeignKey(User, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
\`\`\`

### 🔗 URLs Disponibles

| URL | Vue | Description |
|-----|-----|-------------|
| \`/\` | DashboardView | Tableau de bord principal |
| \`/dashboard/analytics/\` | AnalyticsView | Analytics avancées |
| \`/dashboard/chart-data/\` | ChartDataView | API données graphiques |

---

## 🔐 Système de Permissions

### Hiérarchie des Rôles

\`\`\`
┌─────────────────────────────────────────┐
│              ADMIN                      │
│  ✓ Accès complet                       │
│  ✓ Gestion utilisateurs                │
│  ✓ Configuration système                │
│  ✓ Toutes les fonctionnalités          │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│             MANAGER                     │
│  ✓ Gestion produits                    │
│  ✓ Gestion stocks                      │
│  ✓ Gestion ventes/achats               │
│  ✓ Rapports et analytics               │
│  ✗ Gestion utilisateurs                │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│             CASHIER                     │
│  ✓ Interface de caisse                 │
│  ✓ Créer ventes                        │
│  ✓ Consulter produits                  │
│  ✗ Modifier produits                   │
│  ✗ Gestion stocks                      │
│  ✗ Rapports financiers                 │
└─────────────────────────────────────────┘
\`\`\`

### Décorateurs de Permissions

**Fichier : \`apps/users/decorators.py\`**

\`\`\`python
# Restriction par rôle
@admin_required
def admin_only_view(request):
    pass

@manager_or_admin_cashier_required
def manager_view(request):
    pass

# Utilisation dans les vues
class ProduitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.role == 'admin'
\`\`\`

---

## 🌐 API REST

### Configuration

**Fichier : \`shop360/settings.py\`**

\`\`\`python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
\`\`\`

### Endpoints Disponibles

| Application | Endpoint | Méthodes | Description |
|-------------|----------|----------|-------------|
| Produits | \`/api/produits/\` | GET, POST | Liste/Créer produits |
| Produits | \`/api/produits/{id}/\` | GET, PUT, DELETE | Détails/Modifier/Supprimer |
| Stock | \`/api/stock/mouvements/\` | GET, POST | Mouvements stock |
| Ventes | \`/api/ventes/\` | GET, POST | Ventes |
| Achats | \`/api/achats/\` | GET, POST | Achats |
| Finance | \`/api/finance/transactions/\` | GET, POST | Transactions |

### Exemple d'Utilisation

\`\`\`javascript
// Récupérer la liste des produits
fetch('/api/produits/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log(data));

// Créer un produit
fetch('/api/produits/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        nom: 'Nouveau Produit',
        categorie: 1,
        prix_achat: 5000,
        prix_vente: 7500,
        quantite_stock: 100
    })
})
.then(response => response.json())
.then(data => console.log(data));
\`\`\`

---

## 🎨 Templates et Frontend

### Structure des Templates

\`\`\`
templates/
├── base.html                   # Template de base avec sidebar
├── users/
│   ├── register.html          # Inscription utilisateur
│   ├── profile.html           # Profil utilisateur
│   ├── user_list.html         # Liste utilisateurs
│   └── user_detail.html       # Détails utilisateur
├── produits/
│   ├── list.html              # Liste produits
│   ├── detail.html            # Détails produit
│   └── form.html              # Formulaire produit
├── stock/
│   ├── list.html              # Liste stocks
│   ├── mouvements.html        # Historique mouvements
│   └── inventaires.html       # Inventaires
├── ventes/
│   ├── caisse.html            # Interface POS ⭐
│   ├── list.html              # Liste ventes
│   ├── detail.html            # Détails vente
│   └── ticket.html            # Ticket de caisse
├── achats/
│   ├── list.html              # Liste achats
│   ├── detail.html            # Détails achat
│   └── fournisseurs.html      # Liste fournisseurs
├── finance/
│   ├── overview.html          # Vue d'ensemble
│   ├── transactions.html      # Liste transactions
│   ├── budgets.html           # Liste budgets
│   └── caisse.html            # Gestion caisse
└── dashboard/
    ├── index.html             # Dashboard principal
    └── analytics.html         # Analytics avancées
\`\`\`

### Template de Base

**Fichier : \`templates/base.html\`**

Fonctionnalités :
- ✅ Sidebar responsive Bootstrap 5
- ✅ Menu de navigation avec icônes
- ✅ Menu utilisateur (profil, déconnexion)
- ✅ Notifications en temps réel
- ✅ Breadcrumbs
- ✅ Messages flash Django

### Technologies Frontend

- **Bootstrap 5** : Framework CSS responsive
- **Chart.js** : Graphiques interactifs
- **JavaScript Vanilla** : Pas de dépendance jQuery
- **Font Awesome / Bootstrap Icons** : Icônes
- **Custom CSS** : Styles personnalisés

---

## ⚡ Fonctionnalités Avancées

### 1. Prix Négociable à la Vente ⭐ NOUVEAU

Permet au caissier de modifier le prix d'un produit lors de la vente.

**Fonctionnement** :
1. Le caissier ajoute un produit au panier (prix standard : 100 000 FCFA)
2. Le client négocie : "Je peux l'avoir à 90 000 ?"
3. Le caissier modifie le prix dans le champ input
4. Le système affiche : "🏷️ Réduction: 10 000 FCFA (-10%)"
5. La vente est enregistrée avec traçabilité complète

**Traçabilité** :
- \`prix_original\` : Prix de vente standard (100 000)
- \`prix_unitaire\` : Prix négocié (90 000)
- \`reduction_accordee\` : 10 000 FCFA
- \`pourcentage_reduction\` : 10%

### 2. Gestion Automatique des Stocks

- ✅ Mise à jour automatique lors des ventes
- ✅ Mise à jour automatique lors des achats
- ✅ Historique complet des mouvements
- ✅ Alertes de stock faible
- ✅ Inventaires physiques

### 3. Suivi des Sessions Utilisateurs

- ✅ Enregistrement des connexions/déconnexions
- ✅ Sessions actives en temps réel
- ✅ Présence quotidienne
- ✅ Statistiques d'activité

### 4. Exports Multiples

- ✅ Export CSV (ventes, achats, transactions)
- ✅ Export Excel avec formatage
- ✅ Génération de tickets PDF
- ✅ Rapports financiers

### 5. Interface de Caisse Moderne

- ✅ Recherche produits en temps réel
- ✅ Filtrage par catégorie
- ✅ Panier interactif
- ✅ Modification des quantités
- ✅ **Modification des prix (négociation)** ⭐
- ✅ Calcul automatique des totaux
- ✅ Impression ticket
- ✅ Création rapide de produits

### 6. Tableaux de Bord Interactifs

- ✅ KPIs en temps réel
- ✅ Graphiques Chart.js
- ✅ Top produits vendus
- ✅ Alertes stock
- ✅ Évolution des ventes

---

## 📊 Schéma de Base de Données

\`\`\`mermaid
erDiagram
    User ||--o{ Vente : "vendeur"
    User ||--o{ Achat : "utilisateur"
    User ||--o{ Transaction : "utilisateur"
    User ||--o{ MouvementStock : "utilisateur"
    
    Categorie ||--o{ Produit : "categorie"
    
    Produit ||--o{ VenteItem : "produit"
    Produit ||--o{ AchatItem : "produit"
    Produit ||--o{ MouvementStock : "produit"
    Produit ||--o{ InventaireItem : "produit"
    
    Vente ||--o{ VenteItem : "vente"
    Vente ||--o| Transaction : "vente"
    
    Achat ||--o{ AchatItem : "achat"
    Achat ||--o| Transaction : "achat"
    
    Fournisseur ||--o{ Achat : "fournisseur"
    
    Inventaire ||--o{ InventaireItem : "inventaire"
\`\`\`

---

## 🚀 Installation et Démarrage

### Prérequis

- Python 3.11+
- pip
- virtualenv (recommandé)

### Installation

\`\`\`bash
# Cloner le projet
cd /home/exemplesy/exempleshop360/project

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
\`\`\`

### Accès

- **Application** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **API** : http://127.0.0.1:8000/api/

---

## 📝 Notes Importantes

### Sécurité

- ✅ Protection CSRF activée
- ✅ Authentification requise pour toutes les vues
- ✅ Permissions basées sur les rôles
- ✅ Validation des données côté serveur
- ✅ Sanitization des inputs

### Performance

- ✅ Utilisation de \`select_related\` et \`prefetch_related\`
- ✅ Pagination des listes
- ✅ Indexation des champs fréquemment recherchés
- ✅ Cache des requêtes répétitives

### Maintenance

- ✅ Logs Django configurés
- ✅ Gestion des erreurs
- ✅ Migrations de base de données versionnées
- ✅ Code commenté et documenté

---

## 🎯 Prochaines Fonctionnalités

- [ ] Notifications push en temps réel
- [ ] Rapports PDF personnalisables
- [ ] Intégration paiement mobile (Orange Money, Wave)
- [ ] Application mobile (Flutter)
- [ ] Multi-boutiques
- [ ] Synchronisation cloud
- [ ] Gestion des promotions automatiques
- [ ] Programme de fidélité clients

---
