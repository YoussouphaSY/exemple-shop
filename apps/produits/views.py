from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Produit, Categorie
from .forms import ProduitForm, CategorieForm
from apps.users.decorators import manager_or_admin_cashier_required
from django.utils.decorators import method_decorator


@method_decorator(manager_or_admin_cashier_required, name='dispatch')
class ProduitListView(LoginRequiredMixin, ListView):
    model = Produit
    template_name = 'produits/list.html'
    context_object_name = 'produits'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Produit.objects.filter(actif=True).select_related('categorie')
        
        # Filtre texte
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
        context['categories'] = Categorie.objects.all()
        context['stock_critique'] = Produit.objects.filter(
            actif=True, quantite_stock__lte=F('seuil_alerte')
        ).count()
        return context

class ProduitDetailView(LoginRequiredMixin, DetailView):
    model = Produit
    template_name = 'produits/detail.html'
    context_object_name = 'produit'


class ProduitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'produits/form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        messages.success(self.request, 'Produit créé avec succès!')
        return super().form_valid(form)


class ProduitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'produits/form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        messages.success(self.request, 'Produit modifié avec succès!')
        return super().form_valid(form)


class ProduitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Produit
    template_name = 'produits/confirm_delete.html'
    success_url = reverse_lazy('produits:list')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produit supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class ProduitQuickCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def post(self, request):
        from .forms import ProduitQuickForm
        form = ProduitQuickForm(request.POST)
        if form.is_valid():
            produit = form.save()
            return JsonResponse({
                'success': True,
                'produit': {
                    'id': produit.id,
                    'nom': produit.nom,
                    'prix_vente': str(produit.prix_vente),
                    'quantite_stock': produit.quantite_stock
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })


class CategorieListView(LoginRequiredMixin, ListView):
    model = Categorie
    template_name = 'produits/categories.html'
    context_object_name = 'categories'


class CategorieCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Categorie
    form_class = CategorieForm
    template_name = 'produits/category_form.html'
    success_url = reverse_lazy('produits:categories')
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']