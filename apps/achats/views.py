from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import csv
from openpyxl import Workbook
from .models import Achat, AchatItem, Fournisseur
from .forms import AchatForm, AchatItemFormSet, FournisseurForm, FournisseurQuickForm
from apps.produits.models import Categorie
from apps.users.decorators import manager_or_admin_cashier_required
from django.utils.decorators import method_decorator


@method_decorator(manager_or_admin_cashier_required, name='dispatch')
class AchatListView(LoginRequiredMixin, ListView):
    model = Achat
    template_name = 'achats/list.html'
    context_object_name = 'achats'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Achat.objects.select_related('fournisseur', 'utilisateur')
        
        # Filter by status
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuts'] = Achat.STATUT_CHOICES
        
        # Statistics
        context['total_achats'] = Achat.objects.count()
        context['total_facture'] = Achat.objects.filter(statut='facture').aggregate(
            total=Sum('total_ttc')
        )['total'] or 0
        
        return context


class AchatDetailView(LoginRequiredMixin, DetailView):
    model = Achat
    template_name = 'achats/detail.html'
    context_object_name = 'achat'


class AchatCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Achat
    form_class = AchatForm
    template_name = 'achats/form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fournisseurs'] = Fournisseur.objects.filter(actif=True)
        context['categories'] = Categorie.objects.all()
        if self.request.POST:
            context['formset'] = AchatItemFormSet(self.request.POST)
        else:
            context['formset'] = AchatItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.utilisateur = self.request.user
            self.object.save()
            
            formset.instance = self.object
            formset.save()
            
            messages.success(self.request, 'Achat créé avec succès!')
            return redirect('achats:detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)


class AchatUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Achat
    form_class = AchatForm
    template_name = 'achats/form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AchatItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = AchatItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.save()
            
            messages.success(self.request, 'Achat modifié avec succès!')
            return redirect('achats:detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)


class RecevoirAchatView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def post(self, request, pk):
        achat = get_object_or_404(Achat, pk=pk)
        
        try:
            achat.recevoir()
            messages.success(request, 'Achat marqué comme reçu!')
        except Exception as e:
            messages.error(request, f'Erreur: {e}')
        
        return redirect('achats:detail', pk=pk)


class FacturerAchatView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def post(self, request, pk):
        achat = get_object_or_404(Achat, pk=pk)
        
        try:
            achat.facturer()
            messages.success(request, 'Achat facturé avec succès!')
        except Exception as e:
            messages.error(request, f'Erreur: {e}')
        
        return redirect('achats:detail', pk=pk)


class FournisseurListView(LoginRequiredMixin, ListView):
    model = Fournisseur
    template_name = 'achats/fournisseurs.html'
    context_object_name = 'fournisseurs'


class FournisseurDetailView(LoginRequiredMixin, DetailView):
    model = Fournisseur
    template_name = 'achats/fournisseur_detail.html'
    context_object_name = 'fournisseur'


class FournisseurCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'achats/fournisseur_form.html'
    success_url = reverse_lazy('achats:fournisseurs')
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']


@method_decorator(csrf_exempt, name='dispatch')
class FournisseurQuickCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def post(self, request):
        form = FournisseurQuickForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            return JsonResponse({
                'success': True,
                'fournisseur': {
                    'id': fournisseur.id,
                    'nom': fournisseur.nom,
                    'contact': fournisseur.contact
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })


class ExportAchatsView(LoginRequiredMixin, View):
    def get(self, request):
        format_export = request.GET.get('format', 'csv')
        
        if format_export == 'excel':
            return self.export_excel()
        else:
            return self.export_csv()
    
    def export_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="achats.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Numéro', 'Fournisseur', 'Date', 'Statut', 'Total TTC'])
        
        for achat in Achat.objects.select_related('fournisseur'):
            writer.writerow([
                achat.numero,
                achat.fournisseur.nom,
                achat.date_achat.strftime('%d/%m/%Y'),
                achat.get_statut_display(),
                achat.total_ttc
            ])
        
        return response
    
    def export_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Achats"
        
        # Headers
        headers = ['Numéro', 'Fournisseur', 'Date', 'Statut', 'Total TTC']
        ws.append(headers)
        
        # Data
        for achat in Achat.objects.select_related('fournisseur'):
            ws.append([
                achat.numero,
                achat.fournisseur.nom,
                achat.date_achat.strftime('%d/%m/%Y'),
                achat.get_statut_display(),
                float(achat.total_ttc)
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="achats.xlsx"'
        wb.save(response)
        
        return response