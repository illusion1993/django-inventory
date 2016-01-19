"""Inventory app views"""
from django.contrib import auth, messages
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic import (
    View,
    RedirectView,
    DetailView,
    UpdateView,
    CreateView,
    ListView,
    TemplateView)

from inventory.models import (
    Provision,
    Item,
    User)
from inventory.forms import (
    ProfileUpdateForm,
    AddItemForm,
    EditItemForm,
    RequestItemForm,
    ProvisionItemForm,
    ProvisionItemByRequestForm)


def check_access(arg):
    """Function to check access level and raise 404"""
    if arg:
        return True
    else:
        raise Http404


class LoginView(View):
    """View for login page"""

    def get(self, request):
        """Get method for login page"""
        if request.user.is_authenticated():
            messages.warning(request, 'You are already Logged In')
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            if request.GET.get('next'):
                messages.warning(request, 'You need to login First')

            return TemplateResponse(request, 'login.html')

    def post(self, request):
        """Post method for login page"""
        if request.user.is_authenticated():
            messages.warning(request, 'You are already Logged In')
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)

            if user:
                auth.login(request, user)
                messages.success(request, "You have been logged in")
                print request.GET.get('next')
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                messages.warning(request, "Please check your credentials")
                return TemplateResponse(
                    request, 'login.html', {'email': email})


class LogoutView(RedirectView):
    """View for logout"""

    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        """Processing get request to log a user out"""
        url = self.get_redirect_url(*args, **kwargs)
        if request.user.is_authenticated():
            auth.logout(request)
            messages.success(request, "You have been logged out")
        else:
            raise Http404()

        return HttpResponseRedirect(url)


class DashboardView(TemplateView):
    """View for dashboard page"""

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """Fetching pending and approved requests for context"""
        user = self.request.user
        provisions = Provision.objects.all()
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


class ProfileUpdateView(UpdateView):
    """View for profile update page"""

    model = User
    form_class = ProfileUpdateForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        """Fetching user profile for editing"""
        obj = User.objects.get(id=self.request.user.id)
        return obj


class ItemsView(ListView):
    """View for list of items"""

    model = Item
    context_object_name = 'item_list'
    template_name = 'item_list.html'


class AddItemView(CreateView):
    """View for creating new item"""

    model = Item
    form_class = AddItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('items_list')

    def form_valid(self, form):
        """Save new item, pass message and send mail"""
        messages.success(
            self.request,
            form.cleaned_data['name'] + " has been added to inventory"
        )
        subject = "Inventory Item Added"
        body = form.cleaned_data['name'] + \
            " has been added to the inventory. Quantity added is " + \
            str(form.cleaned_data['quantity'])
        recipients = []

        for user in User.objects.all():
            recipients.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients).send()
        return super(AddItemView, self).form_valid(form)


class EditItemsListView(ListView):
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
        """Update item in db, pass message and send mail"""
        messages.success(
            self.request,
            form.instance.name + " has been updated successfully"
        )
        subject = "Inventory Item Updated"
        body = "Inventory Item - " + form.instance.name + " has been updated."
        recipients = []

        for user in User.objects.filter(is_admin=True):
            recipients.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients).send()
        return super(EditItemView, self).form_valid(form)


class RequestItemView(CreateView):
    """View for requesting an item"""

    template_name = 'request_item.html'
    form_class = RequestItemForm
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """Get the info about requesting user and send it to form"""
        initial = super(RequestItemView, self).get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form):
        """Pass message and save request"""
        messages.success(self.request, "Your request has been submitted")
        return super(RequestItemView, self).form_valid(form)


class ProvisionListView(ListView):
    """View for list of provisions to mark returned from"""

    model = Provision
    template_name = 'provision_list.html'


class ReturnItemView(TemplateView):
    """View for returning item"""

    context_object_name = 'provision'
    template_name = 'return_item.html'

    def get_context_data(self, **kwargs):
        """Fetch the provision model object to modify"""
        provision = get_object_or_404(
            Provision,
            id=kwargs['pk'],
            approved=True,
            returned=False
        )
        referrer = self.request.META.get(
            'HTTP_REFERRER') or reverse_lazy('dashboard')

        context = {
            'provision': provision,
            'referrer': referrer
        }

        context['provision'].returned = True
        context['provision'].returned_on = timezone.now()
        context['provision'].save()

        item = context['provision'].item
        item.quantity += 1
        item.save()

        subject = "Inventory Item Marked Returned"
        body = "An inventory item has been returned by " + provision.user.email
        recipients = [str(User.objects.get(id=provision.user.id).email)]
        cc_to = []

        for user in User.objects.filter(is_admin=True):
            cc_to.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc_to).send()
        return context


class ProvisionItemView(CreateView):
    """View for provision item page"""

    template_name = 'provision_item.html'
    form_class = ProvisionItemForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """Pass message, send mail before saving new provision"""
        item_name = form.cleaned_data['item'].name
        user_email = form.cleaned_data['user'].email
        messages.success(
            self.request,
            item_name + " provisioned to " + user_email
        )

        subject = "Inventory Item Provisioned"
        body = "An inventory item has been provisioned to a user. User - " \
               + user_email \
               + ", item - " \
               + item_name

        recipients = [str(form.instance.user.email)]
        cc_to = []

        for user in User.objects.filter(is_admin=True):
            cc_to.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc_to).send()
        return super(ProvisionItemView, self).form_valid(form)


class ProvisionItemByRequestView(UpdateView):
    """View for accepting provision request"""

    model = Provision
    template_name = 'provision_item_request.html'
    form_class = ProvisionItemByRequestForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """Pass message, send mail before updating provision model object"""
        item_name = form.cleaned_data['item'].name
        user_email = form.instance.user.email
        messages.success(
            self.request,
            item_name + " provisioned to " + user_email
        )
        subject = "Inventory Item Provisioned"
        body = "An inventory item has been provisioned to a user. User - " \
               + user_email \
               + ", item - " \
               + item_name

        recipients = [str(form.instance.user.email)]
        cc_to = []

        for user in User.objects.filter(is_admin=True):
            cc_to.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc_to).send()
        return super(ProvisionItemByRequestView, self).form_valid(form)
