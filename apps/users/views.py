from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegistrationForm, UserUpdateForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:user_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Utilisateur {self.object.username} créé avec succès!')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour avec succès!')
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in ['admin', 'manager']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admins_count'] = User.objects.filter(role='admin').count()
        context['managers_count'] = User.objects.filter(role='manager').count()
        context['cashiers_count'] = User.objects.filter(role='cashier').count()
        return context



class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_obj'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'manager']


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_edit.html'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_success_url(self):
        return reverse_lazy('users:user_detail', kwargs={'pk': self.object.pk})