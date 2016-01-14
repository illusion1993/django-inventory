from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, TemplateView, UpdateView, CreateView, FormView
from django.db.models import Q

# Views start

# Views Common to Users and Admins
from manager.forms import AddItemForm, EditItemForm, ProvisionItemForm, NewProvisionItemForm
from manager.models import Item, User


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


class EditProfileView(UpdateView):

    model = 'User'
    fields = ['first_name', 'last_name', 'phone', 'address', 'id_number', 'image']

class DashboardView(TemplateView):

    template_name = 'dashboard.html'


class ItemListView(ListView):

    model = Item
    template_name = 'item_list.html'


# Views Available to Admins Only

class ProvisionItemView(View):

    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def get(self, request, pk = 0):

        if pk == 0:
            form = ProvisionItemForm()
            form.fields["user"].queryset = User.objects.filter(is_admin = False, is_superuser = False)
            form.fields["item"].queryset = Item.objects.filter(~Q(quantity = 0))

            return render(request, 'provision_item.html', {'form' : form})
        else:
            return HttpResponse('Wait')


    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def post(self, request, pk = 0):

        if pk == 0:
            form = ProvisionItemForm(request.POST)
            form.fields["user"].queryset = User.objects.filter(is_admin = False, is_superuser = False)
            form.fields["item"].queryset = Item.objects.filter(~Q(quantity = 0))

            if form.is_valid():

                provision = form.save()

                provision.quantity = 1
                provision.approved = True
                provision.approved_on = timezone.now()
                provision.return_by = timezone.now() + timezone.timedelta(days=7)

                provision.save()

                form = ProvisionItemForm()
                form.fields["user"].queryset = User.objects.filter(is_admin = False, is_superuser = False)
                form.fields["item"].queryset = Item.objects.filter(~Q(quantity = 0))

                messages.success(request, "{0} issued to user {1}" .format(provision.item.name, provision.user.email))
                return render(request, 'provision_item.html', {'form' : form})

            else:

                return render(request, 'provision_item.html', {'form' : form})


        else:
            return HttpResponse('Wait')

'''
class ProvisionItemView(CreateView):

    form_class = ProvisionItemForm
    template_name = 'provision_item.html'

'''


class AddItemView(View):

    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def get(self, request):

        form = AddItemForm()
        return render(request, 'add_item.html', {'form' : form})

    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def post(self, request):

        form = AddItemForm(request.POST)

        if form.is_valid():

            item = form.save()
            item.save()
            form = AddItemForm()
            messages.success(request, "Item {0} saved in the database" .format(item.name))
            return render(request, 'add_item.html', {'form' : form})

        else:

            form = AddItemForm(request.POST)
            return render(request, 'add_item.html', {'form' : form})


'''
class AddItemView(CreateView):

    form_class = AddItemForm
    template_name = 'add_item.html'
'''
class EditItemView(View):

    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def get(self, request, pk = 0):

        if pk == 0:
            items = Item.objects.all()
            return render(request, 'item_list.html', {'object_list' : items})

        else:
            item = get_object_or_404(Item, id = pk)
            form = EditItemForm(instance = item)

            return render(request, 'edit_item.html', {'form' : form, 'item' : item})

    @method_decorator(user_passes_test(lambda user: user.is_admin, '/dashboard/', None))
    def post(self, request, pk = 0):

        item = get_object_or_404(Item, id = pk)
        form = EditItemForm(request.POST, instance=item)

        if form.is_valid():
            item = form.save()
            item.save()

            messages.success(request, "Item updated successfully")

            return render(request, 'edit_item.html', {'form' : form, 'item' : item})

        else:
            return render(request, 'edit_item.html', {'form' : form, 'item' : item})


#class ReturnItemView(UpdateView):




# Views Available to Users Only

#class RequestItemView(CreateView):