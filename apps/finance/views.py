from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from openpyxl import Workbook
from .models import Transaction, Budget, CaisseFonds
from .forms import TransactionForm, BudgetForm, MouvementCaisseForm
from apps.users.decorators import manager_or_admin_cashier_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
import json


from django.db.models.functions import TruncMonth

@method_decorator(manager_or_admin_cashier_required, name='dispatch')
class FinanceOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        debut_mois = today.replace(day=1)
        debut_annee = today.replace(month=1, day=1)
        
        # --- Solde ---
        context['solde_total'] = Transaction.get_solde()
        context['solde_caisse'] = CaisseFonds.get_solde_caisse()
        
        # --- Stats mensuelles & annuelles ---
        context['ca_mois'] = Transaction.get_ca_periode(debut_mois, today)
        context['depenses_mois'] = Transaction.get_depenses_periode(debut_mois, today)
        context['benefice_mois'] = context['ca_mois'] - context['depenses_mois']
        
        context['ca_annee'] = Transaction.get_ca_periode(debut_annee, today)
        context['depenses_annee'] = Transaction.get_depenses_periode(debut_annee, today)
        
        # --- Transactions récentes ---
        context['transactions_recentes'] = Transaction.objects.select_related(
            'utilisateur', 'vente', 'achat'
        )[:10]
        
        # --- Budgets actifs ---
        context['budgets_actifs'] = Budget.objects.filter(
            actif=True,
            periode_debut__lte=today,
            periode_fin__gte=today
        )

        # --- 📊 Données pour le graphique (recettes & dépenses par mois) ---
        transactions = (
            Transaction.objects
            .annotate(mois=TruncMonth('date'))
            .values('mois', 'type')
            .annotate(total=Sum('montant'))
            .order_by('mois')
        )
        labels, recettes, depenses = [], [], []
        for mois in sorted({t['mois'] for t in transactions}):
            labels.append(mois.strftime("%b %Y"))
            recettes.append(float(sum(t['total'] for t in transactions if t['mois'] == mois and t['type'] == 'RECETTE')))
            depenses.append(float(sum(t['total'] for t in transactions if t['mois'] == mois and t['type'] == 'DEPENSE')))

        context['chart_labels'] = labels
        context['chart_recettes'] = recettes
        context['chart_depenses'] = depenses

        context['chart_labels'] = json.dumps(labels)
        context['chart_recettes'] = json.dumps(recettes)
        context['chart_depenses'] = json.dumps(depenses)


        
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finance/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = Transaction.objects.select_related('utilisateur', 'vente', 'achat')
        
        # Filters
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        categorie_filter = self.request.GET.get('categorie')
        if categorie_filter:
            queryset = queryset.filter(categorie=categorie_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = Transaction.TYPE_CHOICES
        context['categories'] = Transaction.CATEGORY_CHOICES
        
        # Summary for filtered results
        qs = self.get_queryset()
        context['total_recettes'] = qs.filter(type='RECETTE').aggregate(
            total=Sum('montant')
        )['total'] or 0
        context['total_depenses'] = qs.filter(type='DEPENSE').aggregate(
            total=Sum('montant')
        )['total'] or 0
        
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'finance/transaction_detail.html'
    context_object_name = 'transaction'


class TransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = reverse_lazy('finance:transactions')
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        messages.success(self.request, 'Transaction créée avec succès!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solde_actuel'] = Transaction.get_solde()
        return context


class TransactionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        messages.success(self.request, 'Transaction modifiée avec succès!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solde_actuel'] = Transaction.get_solde()
        return context
    
    def get_success_url(self):
        return reverse_lazy('finance:transaction_detail', kwargs={'pk': self.object.pk})


class BudgetListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Budget
    template_name = 'finance/budgets.html'
    context_object_name = 'budgets'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']


# BudgetDetailView
class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = Budget
    template_name = 'finance/budget_detail.html'
    context_object_name = 'budget'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les transactions liées par période et catégorie
        categories_list = [cat.strip().lower() for cat in self.object.categories.split(',') if cat.strip()]
        transactions_liees = Transaction.objects.filter(
            date_valeur__range=[self.object.periode_debut, self.object.periode_fin],
            categorie__in=categories_list
        ).order_by('-date')
        
        context['transactions_liees'] = transactions_liees
        return context
# class BudgetDetailView(LoginRequiredMixin, DetailView):
#     model = Budget
#     template_name = 'finance/budget_detail.html'
#     context_object_name = 'budget'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Transactions réellement liées au budget via le ForeignKey
#         context['transactions_liees'] = self.object.transactions.all().order_by('-date')
#         return context

# class BudgetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
#     model = Budget
#     form_class = BudgetForm
#     template_name = 'finance/budget_form.html'
#     success_url = reverse_lazy('finance:budgets')
    
#     def test_func(self):
#         return self.request.user.role in ['admin', 'manager']
    
#     def form_valid(self, form):
#         form.instance.utilisateur = self.request.user
#         messages.success(self.request, 'Budget créé avec succès!')
#         return super().form_valid(form)

class BudgetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance/budget_form.html'
    success_url = reverse_lazy('finance:budgets')
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def form_valid(self, form):
        try:
            form.instance.utilisateur = self.request.user
            form.instance.full_clean()  # exécute la validation du modèle
            messages.success(self.request, 'Budget créé avec succès!')
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)  # ajoute les erreurs au formulaire
            return self.form_invalid(form)

class BudgetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance/budget_form.html'

    def test_func(self):
        return self.request.user.role in ['admin', 'manager']

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        response = super().form_valid(form)

        # Créer une transaction automatique pour "bloquer" le budget
        Transaction.objects.create(
            type='DEPENSE',
            montant=form.instance.montant_prevu,
            categorie='budget',
            description=f"Budget prévu: {form.instance.nom}",
            budget=form.instance,
            utilisateur=self.request.user,
            date_valeur=form.instance.periode_debut
        )

        messages.success(self.request, 'Budget créé et solde mis à jour!')
        return response

    def get_success_url(self):
        return reverse_lazy('finance:budget_detail', kwargs={'pk': self.object.pk})

class CaisseView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/caisse.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solde_caisse'] = CaisseFonds.get_solde_caisse()
        context['mouvements_recents'] = CaisseFonds.objects.select_related('utilisateur').order_by('-date', '-id')[:10]
        return context



class MouvementCaisseView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'finance/mouvement_caisse.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get_context(self, form):
        return {
            'form': form,
            'solde_actuel': CaisseFonds.get_solde_caisse()  # ← ici
        }
    
    def get(self, request):
        form = MouvementCaisseForm()
        return render(request, self.template_name, self.get_context(form))
    
    def post(self, request):
        form = MouvementCaisseForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.utilisateur = request.user
            mouvement.montant_avant = CaisseFonds.get_solde_caisse()
            
            if mouvement.type in ['ouverture', 'approvisionnement']:
                mouvement.montant_apres = mouvement.montant_avant + mouvement.montant
            else:
                mouvement.montant_apres = mouvement.montant_avant - mouvement.montant
            
            mouvement.save()
            messages.success(request, 'Mouvement de caisse enregistré!')
            return redirect('finance:caisse')
        
        return render(request, self.template_name, self.get_context(form))


class RapportFinancierView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'finance/rapport.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from parameters
        today = timezone.now().date()
        date_debut = self.request.GET.get('date_debut', str(today.replace(day=1)))
        date_fin = self.request.GET.get('date_fin', str(today))
        
        # Convert strings to dates
        if isinstance(date_debut, str):
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if isinstance(date_fin, str):
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        
        # Financial data
        context['date_debut'] = date_debut
        context['date_fin'] = date_fin
        
        # Transactions by category
        context['recettes_par_categorie'] = Transaction.objects.filter(
            type='RECETTE',
            date_valeur__range=[date_debut, date_fin]
        ).values('categorie').annotate(
            total=Sum('montant'),
            count=Count('id')
        ).order_by('-total')
        
        context['depenses_par_categorie'] = Transaction.objects.filter(
            type='DEPENSE',
            date_valeur__range=[date_debut, date_fin]
        ).values('categorie').annotate(
            total=Sum('montant'),
            count=Count('id')
        ).order_by('-total')
        
        # Totals
        context['total_recettes'] = sum(item['total'] for item in context['recettes_par_categorie'])
        context['total_depenses'] = sum(item['total'] for item in context['depenses_par_categorie'])
        context['benefice'] = context['total_recettes'] - context['total_depenses']
        
        return context


class ExportFinanceView(LoginRequiredMixin, View):
    def get(self, request):
        format_export = request.GET.get('format', 'csv')
        type_export = request.GET.get('type', 'transactions')
        
        if type_export == 'budgets':
            if format_export == 'excel':
                return self.export_budgets_excel()
            else:
                return self.export_budgets_csv()
        else:
            if format_export == 'excel':
                return self.export_transactions_excel()
            else:
                return self.export_transactions_csv()
    
    def export_transactions_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Montant', 'Catégorie', 'Description'])
        
        for transaction in Transaction.objects.all():
            writer.writerow([
                transaction.date.strftime('%d/%m/%Y'),
                transaction.get_type_display(),
                transaction.montant,
                transaction.get_categorie_display(),
                transaction.description
            ])
        
        return response
    
    def export_transactions_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"
        
        # Headers
        headers = ['Date', 'Type', 'Montant', 'Catégorie', 'Description']
        ws.append(headers)
        
        # Data
        for transaction in Transaction.objects.all():
            ws.append([
                transaction.date.strftime('%d/%m/%Y'),
                transaction.get_type_display(),
                float(transaction.montant),
                transaction.get_categorie_display(),
                transaction.description
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
        wb.save(response)
        
        return response
    
    def export_budgets_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="budgets.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Montant prévu', 'Montant réalisé', 'Écart', 'Période'])
        
        for budget in Budget.objects.all():
            writer.writerow([
                budget.nom,
                budget.montant_prevu,
                budget.montant_realise,
                budget.ecart,
                f"{budget.periode_debut} - {budget.periode_fin}"
            ])
        
        return response
    
    def export_budgets_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Budgets"
        
        # Headers
        headers = ['Nom', 'Montant prévu', 'Montant réalisé', 'Écart', 'Période début', 'Période fin']
        ws.append(headers)
        
        # Data
        for budget in Budget.objects.all():
            ws.append([
                budget.nom,
                float(budget.montant_prevu),
                float(budget.montant_realise),
                float(budget.ecart),
                budget.periode_debut.strftime('%d/%m/%Y'),
                budget.periode_fin.strftime('%d/%m/%Y')
            ])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="budgets.xlsx"'
        wb.save(response)
        
        return response