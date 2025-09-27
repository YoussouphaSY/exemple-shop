from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.urls import reverse_lazy
from apps.achats import models
from apps.produits.models import Produit
from .models import MouvementStock, Inventaire, InventaireItem
from .forms import InventaireForm, AjustementStockForm


class StockListView(LoginRequiredMixin, ListView):
    model = Produit
    template_name = 'stock/list.html'
    context_object_name = 'produits'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Produit.objects.filter(actif=True).select_related('categorie')

        # Filtre recherche texte
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(description__icontains=query) |
                Q(categorie__nom__icontains=query)
            )

        # Filtre catégorie
        categorie_id = self.request.GET.get('categorie')
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_critique'] = Produit.objects.filter(
            actif=True, quantite_stock__lte=F('seuil_alerte')
        )

        # 🔥 Calcul de la valeur totale du stock
        valeur_stock = Produit.objects.filter(actif=True).aggregate(
            total=Sum(F('quantite_stock') * F('prix_vente'))
        )['total'] or 0


        context['valeur_stock'] = valeur_stock
        return context

class MouvementStockListView(LoginRequiredMixin, ListView):
    model = MouvementStock
    template_name = 'stock/mouvements.html'
    context_object_name = 'mouvements'
    paginate_by = 50

    def get_queryset(self):
        queryset = MouvementStock.objects.select_related('produit', 'utilisateur', 'produit__categorie').all()
        
        # Filtres
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        source_filter = self.request.GET.get('source')
        if source_filter:
            queryset = queryset.filter(source=source_filter)
        
        date_debut = self.request.GET.get('date_debut')
        if date_debut:
            queryset = queryset.filter(date__date__gte=date_debut)
        
        date_fin = self.request.GET.get('date_fin')
        if date_fin:
            queryset = queryset.filter(date__date__lte=date_fin)
        
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mouvements = self.get_queryset()

        # Totaux par type
        context['stats'] = {
            'entrees': mouvements.filter(type='ENTREE').aggregate(total=Sum('quantite'))['total'] or 0,
            'sorties': mouvements.filter(type='SORTIE').aggregate(total=Sum('quantite'))['total'] or 0,
            'ajustements': mouvements.filter(type='AJUSTEMENT').aggregate(total=Sum('quantite'))['total'] or 0,
        }

        return context


class InventaireListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Inventaire
    template_name = 'stock/inventaire_list.html'
    context_object_name = 'inventaires'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']


class InventaireCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Inventaire
    form_class = InventaireForm
    template_name = 'stock/inventaire_form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        response = super().form_valid(form)
        
        # Create inventory items for all active products
        for produit in Produit.objects.filter(actif=True):
            InventaireItem.objects.create(
                inventaire=self.object,
                produit=produit,
                quantite_systeme=produit.quantite_stock
            )
        
        messages.success(self.request, 'Inventaire créé avec succès!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('stock:inventaire_detail', kwargs={'pk': self.object.pk})


class InventaireDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Inventaire
    template_name = 'stock/inventaire_detail.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']


class InventaireUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Inventaire
    template_name = 'stock/inventaire_edit.html'
    fields = []
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager'] and not self.get_object().clos
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('produit').all()
        return context
    
    def post(self, request, *args, **kwargs):
        inventaire = self.get_object()
        
        # Update item quantities
        for key, value in request.POST.items():
            if key.startswith('quantite_'):
                item_id = key.split('_')[1]
                try:
                    item = inventaire.items.get(pk=item_id)
                    item.quantite_comptee = int(value or 0)
                    item.save()
                except (InventaireItem.DoesNotExist, ValueError):
                    pass
        
        messages.success(request, 'Quantités mises à jour!')
        return redirect('stock:inventaire_detail', pk=inventaire.pk)


class InventaireCloseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def post(self, request, pk):
        inventaire = get_object_or_404(Inventaire, pk=pk)
        
        if inventaire.clos:
            messages.error(request, 'Inventaire déjà clos!')
        else:
            inventaire.cloturer()
            messages.success(request, 'Inventaire clos avec succès!')
        
        return redirect('stock:inventaire_detail', pk=pk)


class AjustementStockView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'stock/ajustement.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get(self, request):
        form = AjustementStockForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = AjustementStockForm(request.POST)
        if form.is_valid():
            produit = form.cleaned_data['produit']
            quantite = form.cleaned_data['quantite']
            motif = form.cleaned_data['motif']
            
            try:
                MouvementStock.create_mouvement(
                    produit=produit,
                    quantite=quantite,
                    source='ajustement',
                    user=request.user,
                    motif=motif
                )
                messages.success(request, 'Ajustement effectué avec succès!')
                return redirect('stock:list')
            except ValueError as e:
                form.add_error(None, str(e))
        
        return render(request, self.template_name, {'form': form})