from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView
from manager.forms import AddItemForm, EditItemForm, RequestItemForm, ReturnItemForm
from manager.models import Item, Provision


class LoginView(View):

    @method_decorator(user_passes_test(lambda user: not user.is_authenticated(), '/dashboard/', None))
    def get(self, request):

        return render(request, "login.html")

    @method_decorator(user_passes_test(lambda user: not user.is_authenticated(), '/dashboard/', None))
    def post(self, request):

        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(email = email, password = password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/dashboard/')

        else:
            messages.warning(request, "login failed")
            return render(request, "login.html")


class LogoutView(View):

    @method_decorator(user_passes_test(lambda user: user.is_authenticated(), '/login/', None))
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login/')

    @method_decorator(user_passes_test(lambda user: user.is_authenticated(), '/login/', None))
    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/login/')

class DashboardView(View):

    def get(self, request):
        return HttpResponse('Dashboard')


class ItemsView(ListView):

    model = Item
    context_object_name = 'item_list'
    template_name = 'item_list.html'

class AddItemView(CreateView):

    model = Item
    form_class = AddItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('items_list')

class EditItemView(UpdateView):

    model = Item
    template_name = 'edit_item.html'
    form_class = EditItemForm
    success_url = reverse_lazy('items_list')

class RequestItemView(CreateView):

    model = Provision
    template_name = 'request_item.html'
    form_class = RequestItemForm
    success_url = reverse_lazy('dashboard')

class ProvisionListView(ListView):

    model = Provision
    template_name = 'provision_list.html'

class ReturnItemView(UpdateView):

    model = Provision
    template_name = 'return_item.html'
    form_class = ReturnItemForm
    success_url = reverse_lazy('provision_list')