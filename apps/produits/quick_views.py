from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Categorie
from .forms import CategorieForm

@method_decorator(csrf_exempt, name='dispatch')
class CategorieQuickCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['admin', 'manager', 'Administrateur', 'Gestionnaire']
    
    def post(self, request):
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        
        if not nom:
            return JsonResponse({'success': False, 'errors': {'nom': ['Ce champ est obligatoire.']}})
            
        if Categorie.objects.filter(nom__iexact=nom).exists():
             return JsonResponse({'success': False, 'errors': {'nom': ['Cette catégorie existe déjà.']}})
        
        try:
            categorie = Categorie.objects.create(nom=nom, description=description)
            return JsonResponse({
                'success': True,
                'categorie': {
                    'id': categorie.id,
                    'nom': categorie.nom
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'errors': {'non_field_errors': [str(e)]}})
