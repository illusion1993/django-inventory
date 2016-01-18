import smtplib
from django import http
from django.contrib import auth, messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, RedirectView, DetailView, UpdateView, CreateView, \
    ListView
from inventory.forms import ProfileUpdateForm, AddItemForm, EditItemForm, RequestItemForm, ProvisionItemForm, \
    ProvisionItemByRequestForm
from inventory.models import Provision, User, Item

# Method to return 404 is access is not allowed for user type
def check_access(arg):
    if arg:
        return True
    else:
        raise Http404

class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already Logged In')
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            if request.GET.get('next'):
                messages.warning(request, 'You need to login First')

            return TemplateResponse(request, 'login.html')

    def post(self, request):
        if request.user.is_authenticated():
            messages.warning(request, 'You are already Logged In')
            return HttpResponseRedirect(reverse_lazy('dashboard'))

        else:
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)
            if user:
                    auth.login(request, user)
                    messages.success(request, "You have been logged in successfully")
                    print request.GET.get('next')
                    if request.GET.get('next'):
                        return HttpResponseRedirect(request.GET['next'])
                    else:
                        return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                messages.warning(request, "Please check your credentials")
                return TemplateResponse(request, 'login.html', {'email' : email})

class LogoutView(RedirectView):

    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if request.user.is_authenticated():
            logout(request)
            messages.success(request, "You have been logged out")
        else:
            raise Http404()

        return HttpResponseRedirect(url)

class DashboardView(TemplateView):

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):

        #send_mail('Subject here', 'Here is the message.', 'Django Inventory App', ['vikram.rathore@joshtechnologygroup.com'], fail_silently=False)

        is_admin = self.request.user.is_admin
        is_user = self.request.user.is_authenticated() and not self.request.user.is_admin
        context = {'is_admin' : is_admin, 'is_user' : is_user}

        if is_admin:
            pending = Provision.objects.filter(approved=False).order_by('timestamp')
            approved = Provision.objects.filter(approved=True, returned=False).order_by('-timestamp')

        else:
            pending = Provision.objects.filter(user=self.request.user, approved=False).order_by('timestamp')
            approved = Provision.objects.filter(user=self.request.user, approved=True).order_by('timestamp')

        context['pending'] = pending
        context['approved'] = approved

        return context

class ProfileView(DetailView):

    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        obj = User.objects.get(id=self.request.user.id)
        return obj


class ProfileUpdateView(UpdateView):

    model = User
    form_class = ProfileUpdateForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        obj = User.objects.get(id=self.request.user.id)
        return obj


class ItemsView(ListView):

    model = Item
    context_object_name = 'item_list'
    template_name = 'item_list.html'

class AddItemView(CreateView):

    model = Item
    form_class = AddItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('items_list')

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(AddItemView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, form.cleaned_data['name'] + " has been added to inventory")

        subject = "Inventory Item Added"
        body = "A new item named " + form.cleaned_data['name'] + " has been added to the inventory. Quantity added is " + str(form.cleaned_data['quantity'])
        recipients = []

        for user in User.objects.all():
            recipients.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients).send()

        return super(AddItemView, self).form_valid(form)

class EditItemsListView(ListView):

    model = Item
    context_object_name = 'item_list'
    template_name = 'edit_item_list.html'

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(EditItemsListView, self).dispatch(*args, **kwargs)

class EditItemView(UpdateView):

    model = Item
    template_name = 'edit_item.html'
    form_class = EditItemForm
    success_url = reverse_lazy('edit_item_list')

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(EditItemView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, form.instance.name + " has been updated successfully")

        subject = "Inventory Item Updated"
        body = "An inventory item has been updated. Item name - " + form.instance.name
        recipients = []

        for user in User.objects.filter(is_admin=True):
            recipients.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients).send()

        return super(EditItemView, self).form_valid(form)

class RequestItemView(CreateView):

    template_name = 'request_item.html'
    form_class = RequestItemForm
    success_url = reverse_lazy('dashboard')

    @method_decorator(user_passes_test(lambda user: check_access(not user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(RequestItemView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(RequestItemView, self).get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Your request has been submitted")
        return super(RequestItemView, self).form_valid(form)

class ProvisionListView(ListView):

    model = Provision
    template_name = 'provision_list.html'

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(ProvisionListView, self).dispatch(*args, **kwargs)

class ReturnItemView(TemplateView):

    context_object_name = 'provision'
    template_name = 'return_item.html'

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(ReturnItemView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        provision = get_object_or_404(Provision, id=kwargs['pk'], approved=True, returned=False)
        referrer = self.request.META.get('HTTP_REFERER') or reverse_lazy('dashboard')

        context = {'provision': provision, 'referrer': referrer}

        context['provision'].returned = True
        context['provision'].returned_on = timezone.now()
        context['provision'].save()

        item = context['provision'].item
        item.quantity += 1
        item.save()

        subject = "Inventory Item Marked Returned"
        body = "An inventory item has been returned by " + provision.user.email
        recipients = [str(User.objects.get(id=provision.user.id).email)]
        cc = []

        for user in User.objects.filter(is_admin=True):
            cc.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc).send()

        return context

class ProvisionItemView(CreateView):

    template_name = 'provision_item.html'
    form_class = ProvisionItemForm
    success_url = reverse_lazy('dashboard')

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(ProvisionItemView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, form.cleaned_data['item'].name + " has been provisioned to " + form.cleaned_data['user'].email)

        subject = "Inventory Item Provisioned"
        body = "An inventory item has been provisioned to a user. User - " + form.instance.user.email + ", item - " + form.instance.item.name
        recipients = [str(form.instance.user.email)]
        cc = []

        for user in User.objects.filter(is_admin=True):
            cc.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc).send()

        return super(ProvisionItemView, self).form_valid(form)

class ProvisionItemByRequestView(UpdateView):

    model = Provision
    template_name = 'provision_item_request.html'
    form_class = ProvisionItemByRequestForm
    success_url = reverse_lazy('dashboard')

    @method_decorator(user_passes_test(lambda user: check_access(user.is_admin)))
    def dispatch(self, *args, **kwargs):
        return super(ProvisionItemByRequestView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, form.cleaned_data['item'].name + " has been provisioned to " + form.instance.user.email)

        subject = "Inventory Item Provisioned"
        body = "An inventory item has been provisioned to a user. User - " + form.instance.user.email + ", item - " + form.instance.item.name
        recipients = [str(form.instance.user.email)]
        cc = []

        for user in User.objects.filter(is_admin=True):
            cc.append(str(user.email))

        EmailMessage(subject=subject, body=body, to=recipients, cc=cc).send()

        return super(ProvisionItemByRequestView, self).form_valid(form)