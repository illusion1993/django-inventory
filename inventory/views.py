"""Inventory app views"""

from django.contrib import auth, messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import (
    View,
    RedirectView,
    DetailView,
    UpdateView,
    CreateView,
    ListView,
    TemplateView, FormView)

from inventory.models import (
    Provision,
    Item,
    User)
from inventory.forms import (
    EditProfileForm,
    AddItemForm,
    EditItemForm,
    RequestItemForm,
    ProvisionItemForm,
    ProvisionItemByRequestForm, ReturnItemForm)
from inventory.message_constants import *


class LoginView(View):
    """View for login page"""

    def get(self, request):
        """Get method for login page"""
        if request.user.is_authenticated():
            messages.warning(request, ALREADY_LOGGED_MESSAGE)
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            if request.GET.get('next'):
                messages.warning(request, LOGIN_REQUIRED_MESSAGE)

            return TemplateResponse(request, 'login.html')

    def post(self, request):
        """Post method for login page"""
        if request.user.is_authenticated():
            messages.warning(request, ALREADY_LOGGED_MESSAGE)
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)

            if user:
                auth.login(request, user)
                messages.success(request, LOGIN_SUCCESS_MESSAGE)
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                messages.warning(request, LOGIN_INVALID_MESSAGE)
                return TemplateResponse(
                    request, 'login.html', {'email': email})


class LogoutView(RedirectView):
    """View for logout"""

    url = reverse_lazy('login')
    permanent = False
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        """Processing get request to log a user out"""
        url = self.get_redirect_url(*args, **kwargs)
        if request.user.is_authenticated():
            auth.logout(request)
            messages.success(request, LOGOUT_SUCCESS_MESSAGE)
        else:
            raise Http404()

        return HttpResponseRedirect(url)


class DashboardView(TemplateView):
    """View for dashboard page"""

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """Fetching pending and approved requests for context"""
        user = self.request.user
        provisions = Provision.objects.filter(returned=False)
        is_admin = user.is_admin
        is_user = user.is_authenticated() and not user.is_admin
        context = {
            'is_admin': is_admin,
            'is_user': is_user
        }

        if is_admin:
            pending = provisions.filter(approved=False).order_by('timestamp')
            approved = provisions.filter(
                approved=True,
                returned=False
            ).order_by('-timestamp')

        else:
            pending = provisions.filter(
                user=self.request.user,
                approved=False
            ).order_by('timestamp')
            approved = provisions.filter(
                user=self.request.user,
                approved=True
            ).order_by('-timestamp')

        context['pending'] = pending
        context['approved'] = approved
        return context


class ProfileView(DetailView):
    """View for profile page"""

    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        """Fetching user profile for viewing"""
        obj = User.objects.get(id=self.request.user.id)
        return obj


class EditProfileView(FormView):
    """View for profile update page"""

    template_name = 'edit_profile.html'
    form_class = EditProfileForm
    success_url = reverse_lazy('profile')

    def get_form(self, form_class):
        """Load the form with the instance of user model object"""
        ins = User.objects.get(id=self.request.user.id)
        return form_class(instance=ins, **self.get_form_kwargs())

    def form_valid(self, form):
        """If the form is valid, save the object in db"""
        form.save()
        return super(EditProfileView, self).form_valid(form)


class ItemsListView(ListView):
    """View for list of items"""

    model = Item
    context_object_name = 'item_list'
    template_name = 'items_list.html'


class AddItemView(CreateView):
    """View for creating new item"""

    model = Item
    form_class = AddItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('items_list')

    def form_valid(self, form):
        """Adding message when form is validated"""
        messages.success(
            self.request,
            item_added_message(form.cleaned_data['name'])
        )

        return super(AddItemView, self).form_valid(form)


class EditItemListView(ListView):
    """View for list of items to edit from"""

    model = Item
    context_object_name = 'item_list'
    template_name = 'edit_item_list.html'


class EditItemView(UpdateView):
    """View for item editing"""

    model = Item
    template_name = 'edit_item.html'
    form_class = EditItemForm
    success_url = reverse_lazy('edit_item_list')

    def form_valid(self, form):
        """Adding message when item is updated"""
        messages.success(
            self.request,
            item_edited_message(form.instance.name)
        )

        return super(EditItemView, self).form_valid(form)


class RequestItemView(FormView):
    """View for requesting an item"""

    template_name = 'request_item.html'
    form_class = RequestItemForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """Save provision object, Pass message and save request"""
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, REQUEST_SUBMITTED_MESSAGE)
        return super(RequestItemView, self).form_valid(form)


class ProvisionListView(ListView):
    """View for list of provisions to mark returned from"""

    model = Provision
    template_name = 'provision_list.html'

    def get_queryset(self):
        """Changing queryset to view only non returned provisions"""
        self.queryset = self.model.objects.filter(returned=False)
        return super(ProvisionListView, self).get_queryset()


class ReturnItemView(UpdateView):
    """View for returning item"""

    model = Provision
    form_class = ReturnItemForm
    template_name = 'return_item.html'
    success_url = reverse_lazy('provision_list')

    def get_object(self, queryset=None):
        """Get provision object from the database, give 404 if not found"""
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(
            Provision,
            id=pk,
            approved=True,
            returned=False,
            )

        return obj

    def form_valid(self, form):
        """Passing success message when form is validated"""
        user = form.instance.user.email
        item = form.instance.item.name

        messages.success(
            self.request,
            ITEM_RETURNED_MESSAGE
        )

        return super(ReturnItemView, self).form_valid(form)


class ProvisionItemView(FormView):
    """View for provision item page"""

    template_name = 'provision_item.html'
    form_class = ProvisionItemForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """Give success message when form is validated"""

        item_name = form.instance.item.name
        user_email = form.instance.user.email
        messages.success(
            self.request,
            item_provision_message(item_name, user_email)
        )

        return super(ProvisionItemView, self).form_valid(form)


class ProvisionByRequestView(UpdateView):
    """View for accepting provision request"""

    model = Provision
    template_name = 'provision_by_request.html'
    form_class = ProvisionItemByRequestForm
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        """Get provision object from the database, give 404 if not found"""
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(Provision, id=pk, approved=False)
        return obj

    def form_valid(self, form):
        """Pass success message when form is validated"""
        messages.success(
            self.request,
            item_provision_message(form.instance.item.name, form.instance.user.email)
        )

        return super(ProvisionByRequestView, self).form_valid(form)
