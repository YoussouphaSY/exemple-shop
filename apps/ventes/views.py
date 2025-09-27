from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
from openpyxl import Workbook
from .models import Vente, VenteItem
from .forms import VenteForm, VenteItemFormSet
from apps.produits.models import Produit
from apps.users.decorators import cashier_access
from django.utils.decorators import method_decorator


class VenteListView(LoginRequiredMixin, ListView):
    model = Vente
    template_name = 'ventes/list.html'
    context_object_name = 'ventes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vente.objects.select_related('vendeur')
        
        # Filter by date range
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        
        if date_debut:
            queryset = queryset.filter(date_vente__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_vente__date__lte=date_fin)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        today = timezone.now().date()
        context['ventes_aujourd_hui'] = Vente.objects.filter(date_vente__date=today).count()
        context['ca_aujourd_hui'] = Vente.objects.filter(
            date_vente__date=today
        ).aggregate(total=Sum('total_ttc'))['total'] or 0
        
        return context


class VenteDetailView(LoginRequiredMixin, DetailView):
    model = Vente
    template_name = 'ventes/detail.html'
    context_object_name = 'vente'


class VenteCreateView(LoginRequiredMixin, CreateView):
    model = Vente
    form_class = VenteForm
    template_name = 'ventes/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = VenteItemFormSet(self.request.POST)
        else:
            context['formset'] = VenteItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.vendeur = self.request.user
            self.object.save()
            
            formset.instance = self.object
            formset.save()
            
            messages.success(self.request, 'Vente créée avec succès!')
            return redirect('ventes:detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)


class VenteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vente
    form_class = VenteForm
    template_name = 'ventes/form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = VenteItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = VenteItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.save()
            
            messages.success(self.request, 'Vente modifiée avec succès!')
            return redirect('ventes:detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)


@method_decorator(cashier_access, name='dispatch')
class CaisseView(LoginRequiredMixin, View):
    template_name = 'ventes/caisse.html'
    
    def get(self, request):
        produits = Produit.objects.filter(actif=True, quantite_stock__gt=0).select_related('categorie')
        return render(request, self.template_name, {'produits': produits})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Create sale
            vente = Vente.objects.create(
                client=data.get('client', ''),
                telephone_client=data.get('telephone', ''),
                mode_paiement=data.get('mode_paiement', 'especes'),
                vendeur=request.user
            )
            
            # Create sale items
            for item_data in data['items']:
                produit = Produit.objects.get(pk=item_data['produit_id'])
                VenteItem.objects.create(
                    vente=vente,
                    produit=produit,
                    quantite=item_data['quantite'],
                    prix_unitaire=item_data['prix_unitaire']
                )
            
            # Finalize sale
            vente.finaliser()
            
            return JsonResponse({
                'success': True,
                'vente_id': vente.pk,
                'numero': vente.numero
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class FinalizeVenteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vente = get_object_or_404(Vente, pk=pk)
        
        try:
            vente.finaliser()
            messages.success(request, 'Vente finalisée avec succès!')
        except Exception as e:
            messages.error(request, f'Erreur lors de la finalisation: {e}')
        
        return redirect('ventes:detail', pk=pk)


class TicketView(LoginRequiredMixin, DetailView):
    model = Vente
    template_name = 'ventes/ticket.html'
    context_object_name = 'vente'


class ExportVentesView(LoginRequiredMixin, View):
    def get(self, request):
        format_export = request.GET.get('format', 'csv')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        queryset = Vente.objects.all()
        
        if date_debut:
            queryset = queryset.filter(date_vente__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_vente__date__lte=date_fin)
        
        if format_export == 'excel':
            return self.export_excel(queryset)
        else:
            return self.export_csv(queryset)
    
    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ventes.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Numéro', 'Date', 'Client', 'Total TTC', 'Mode paiement', 'Vendeur'])
        
        for vente in queryset:
            writer.writerow([
                vente.numero,
                vente.date_vente.strftime('%d/%m/%Y %H:%M'),
                vente.client,
                vente.total_ttc,
                vente.get_mode_paiement_display(),
                vente.vendeur.get_full_name() if vente.vendeur else ''
            ])
        
        return response
    
    def export_excel(self, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Ventes"
        
        # Headers
        headers = ['Numéro', 'Date', 'Client', 'Total TTC', 'Mode paiement', 'Vendeur']
        ws.append(headers)
        
        # Data
        for vente in queryset:
            ws.append([
                vente.numero,
                vente.date_vente.strftime('%d/%m/%Y %H:%M'),
                vente.client,
                float(vente.total_ttc),
                vente.get_mode_paiement_display(),
                vente.vendeur.get_full_name() if vente.vendeur else ''
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ventes.xlsx"'
        wb.save(response)
        
        return response