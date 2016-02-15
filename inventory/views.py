"""Inventory app views"""
from datetime import datetime
import json

from django.contrib import auth, messages
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse_lazy
from django.db.models import Sum
from django.forms import formset_factory
from django.http import (
    HttpResponseRedirect,
    Http404,
    JsonResponse
)
from django.shortcuts import get_object_or_404
from django.views.generic import (
    View,
    RedirectView,
    DetailView,
    UpdateView,
    CreateView,
    ListView,
    TemplateView,
    FormView
)

from inventory.models import (
    Provision,
    Item,
    User
)
from inventory.forms import (
    EditProfileForm,
    AddItemForm,
    EditItemForm,
    RequestItemForm,
    ProvisionItemForm,
    ProvisionItemByRequestForm,
    ReturnItemForm,
    ImageUploadForm,
    DateFilterForm,
    LoginForm,
    ProvisionFormset
)
from inventory.message_constants import *
from inventory.tasks import send_report

from dal import autocomplete


class LoginFormView(FormView):
    """
    View for login page
    """

    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """
        If for is valid, authenticate user
        """
        # Initialize credentials for authentication
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember = form.cleaned_data['remember']

        # Authenticate user
        user = auth.authenticate(email=email, password=password)

        # If authentication passed, send to dashboard
        if user:
            auth.login(self.request, user)
            messages.success(self.request, LOGIN_SUCCESS_MESSAGE)

            if not remember:
                self.request.session.set_expiry(0)

            if self.request.GET.get('next'):
                return HttpResponseRedirect(self.request.GET['next'])
            else:
                return super(LoginFormView, self).form_valid(form)
        else:
            messages.warning(self.request, LOGIN_INVALID_MESSAGE)
            return super(LoginFormView, self).form_invalid(form)


class LogoutView(RedirectView):
    """
    View for logout
    """

    url = reverse_lazy('login')
    permanent = False
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        """
        Processing get request to log a user out
        """

        url = self.get_redirect_url(*args, **kwargs)

        # If user was authenticated, log out
        if request.user.is_authenticated():
            auth.logout(request)
            messages.success(request, LOGOUT_SUCCESS_MESSAGE)

        # Else raise 404 for anonymous users
        else:
            raise Http404()

        return HttpResponseRedirect(url)


class DashboardView(TemplateView):
    """
    View for dashboard page
    """

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Fetching pending and approved requests for context
        """

        user = self.request.user
        provisions = Provision.objects.filter(returned=False)
        is_admin = user.is_admin
        is_user = user.is_authenticated() and not user.is_admin

        # Assign admin the role of user, if requested
        if user.is_admin and self.request.GET.get('user', False):
            is_admin = False
            is_user = True

        # Store role variables for context
        context = {
            'is_admin': is_admin,
            'is_user': is_user
        }

        if is_admin:
            pending = provisions.filter(
                approved=False,
            ).order_by('timestamp')

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

        if pending.count() > 5:
            pending_more = True
        else:
            pending_more = False

        if approved.count() > 5:
            approved_more = True
        else:
            approved_more = False

        pending = pending[:5]
        approved = approved[:5]

        context['pending'] = pending
        context['approved'] = approved
        context['pending_more'] = pending_more
        context['approved_more'] = approved_more

        return context


class ProfileView(DetailView):
    """
    View for profile page
    """

    model = User
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        """
        Fetching user profile for viewing
        """

        obj = User.objects.get(id=self.request.user.id)
        return obj


class EditProfileView(FormView):
    """
    View for profile update page
    """

    template_name = 'edit_profile.html'
    form_class = EditProfileForm
    success_url = reverse_lazy('profile')

    def get_form(self, form_class):
        """
        Load the form with the instance of user model object
        """

        ins = User.objects.get(id=self.request.user.id)
        return form_class(instance=ins, **self.get_form_kwargs())

    def form_valid(self, form):
        """
        If the form is valid, save the object in db
        """

        form.save()
        return super(EditProfileView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Save both the forms in context
        """

        if 'form2' not in kwargs:
            kwargs['form2'] = PasswordChangeForm(user=self.request.user)
            return super(EditProfileView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        Checking if password form is submitted
        """

        password_form_submitted = request.POST.get('change_password', False)

        if password_form_submitted:
            """Process the password form"""
            form2_kwargs = {
                'data': request.POST,
            }

            form = self.form_class(instance=request.user)
            form2 = PasswordChangeForm(request.user, **form2_kwargs)

            if form2.is_valid():
                # Passing message
                messages.success(
                    request,
                    PASSWORD_CHANGE_SUCCESS_MESSAGE
                )

                # Going to success url
                return self.form_valid(form2)

        else:
            """Process the profile update form"""
            form = self.get_form()
            form2 = PasswordChangeForm(user=self.request.user)

            if form.is_valid():
                # Passing message
                if form.has_changed():
                    messages.success(
                        request,
                        PROFILE_UPDATE_SUCCESS_MESSAGE
                    )

                # Going to success url
                return self.form_valid(form)

            else:
                return self.form_invalid(form)

        context = {
            'form': form,
            'form2': form2
        }

        return self.render_to_response(context)


class ItemsListView(ListView):
    """
    View for list of items
    """

    model = Item
    context_object_name = 'item_list'
    template_name = 'items_list.html'


class AddItemView(CreateView):
    """
    View for creating new item
    """

    model = Item
    form_class = AddItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """Adding message when form is validated"""
        messages.success(
            self.request,
            item_added_message(form.cleaned_data['name'])
        )

        return super(AddItemView, self).form_valid(form)


class EditItemListView(ListView):
    """
    View for list of items to edit from
    """

    model = Item
    context_object_name = 'item_list'
    template_name = 'edit_item_list.html'


class EditItemView(UpdateView):
    """View for item editing"""

    model = Item
    template_name = 'edit_item.html'
    form_class = EditItemForm
    success_url = reverse_lazy('dashboard')

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
    success_url = reverse_lazy('dashboard')

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
    success_url = reverse_lazy('dashboard')

    def form_valid(self, formset):
        """
        If the form is valid, redirect to the supplied URL.
        """

        for form in formset:
            form.save()

        messages.success(
            self.request,
            'Items provisioned successfully'
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, formset):
        context = {
            'formset': formset
        }
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = {
            'formset': formset_factory(ProvisionItemForm, formset=ProvisionFormset, extra=1)
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        ProvisionItemFormset = formset_factory(ProvisionItemForm, formset=ProvisionFormset)
        formset = ProvisionItemFormset(request.POST, request.FILES)

        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)


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
            item_provision_message(
                form.instance.item.name,
                form.instance.user.email
            )
        )

        return super(ProvisionByRequestView, self).form_valid(form)


class PasswordChangeView(FormView):
    template_name = 'change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class LoadMoreView(View):
    """View to load more provisions in the dashboard via ajax"""

    def get(self, request):
        if request.is_ajax():
            """Process AJAX request and send required data"""
            load_more_pending = request.GET.get('load_more_pending', False)
            load_more_approved = request.GET.get('load_more_approved', False)

            provisions = Provision.objects.filter(returned=False)

            if request.user.is_admin and self.request.GET.get('is_admin', False) == 'True':
                is_admin = True
            else:
                is_admin = False

            if is_admin:
                pending = provisions.filter(
                    approved=False,
                ).order_by('timestamp')

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

            pending = pending[5:]
            approved = approved[5:]

            # Load more pending requests
            if load_more_pending:
                p_list = list(pending)
                p_dict = {
                    'pending': []
                }

                for p in p_list:
                    p_dict['pending'].append({
                        'item_name': p.item.name,
                        'description': (p.item.description[:75] + '...') if len(
                            p.item.description) > 75 else p.item.description,
                        'provision_id': p.id
                    })

                return JsonResponse(p_dict)

            # Load more approved requests
            if load_more_approved:
                a_list = list(approved)
                a_dict = {
                    'approved': []
                }

                for a in a_list:
                    a_dict['approved'].append({
                        'provision_id': a.id,
                        'item_name': a.item.name,
                        'description': (a.item.description[:75] + '...') if len(a.item.description) > 75 else a.item.description,
                        'returnable': 'Yes' if a.item.returnable else 'No',
                        'return_by': a.return_by.strftime("%d %b %y") if a.return_by else 'N/A',
                        'user_email': a.user.email,
                        'returned': 'Yes' if a.returned else 'No' if a.item.returnable else 'N/A',
                    })

                return JsonResponse(a_dict)


class ImageUploadView(UpdateView):
    """View to process image upload via AJAX"""
    model = User
    form_class = ImageUploadForm

    def get_object(self, queryset=None):
        """Get user model obj"""
        obj = User.objects.get(id=self.request.user.id)
        return obj

    def post(self, request, *args, **kwargs):

        if request.is_ajax():

            clear = request.POST.get('clear_image', False)
            self.object = self.get_object()
            form = self.get_form()
            form.instance.delete_image()
            form.instance.image = ''

            if not clear:
                if form.is_valid():
                    self.object = form.save()
                    resp = {
                        'success': 'True',
                        'image': form.instance.image.url,
                    }
                else:
                    resp = {
                        'success': 'False',
                        'error': list(form.errors['image']),
                    }
            else:
                form.instance.save()
                resp = {
                    'success': 'True',
                }

            return JsonResponse(resp)


class UserAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs


class ItemAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Item.objects.none()

        qs = Item.objects.exclude(quantity=0)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class ReportView(TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        if 'form' not in kwargs:
            kwargs['form'] = DateFilterForm()
        return kwargs


class ReportAjaxView(View):

    def get(self, request):
        if request.is_ajax():

            # Saving the GET variables to filter data
            returnable = request.GET.get('r', True)
            non_returnable = request.GET.get('nr', True)
            start_date = request.GET.get('sd', '')
            end_date = request.GET.get('ed', '')
            mail_me = request.GET.get('mm', False)

            # Storing all the item and provision objects
            items = Item.objects.all()
            provisions = Provision.objects.filter(approved=True)

            # Cutting down the irrelevant objects, as per filters
            if returnable == 'true' and non_returnable == 'false':
                items = items.filter(returnable=True)
            if non_returnable == 'true' and returnable == 'false':
                items = items.filter(returnable=False)
            if not start_date == '':
                start_date = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
                for provision in provisions:
                    if provision.approved_on < start_date:
                        provisions = provisions.exclude(id=provision.id)
            if not end_date == '':
                end_date = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
                for provision in provisions:
                    if provision.approved_on > end_date:
                        provisions = provisions.exclude(id=provision.id)

            # Storing the final results for response data
            data = []

            for item in items:
                provisions_for_item = provisions.filter(item=item)
                row = {}
                row['name'] = (item.name)
                row['description'] = (item.description)

                if item.returnable:
                    row['returnable'] = 'Yes'

                else:
                    row['returnable'] = 'No'

                count = provisions_for_item.aggregate(Sum('quantity')).get('quantity__sum')
                row['quantity'] = count
                if count:
                    data.append(row)

            resp = {
                "draw": 10,
                "recordsTotal": provisions.count(),
                "recordsFiltered": provisions.count(),
                "data": data
            }

            return JsonResponse(resp)

        else:
            raise Http404()

    def post(self, request):

        if request.is_ajax():
            csv = request.POST.get('csv', '')

            if csv != '':
                csv = {'csv': json.loads(csv)}
                send_report.delay(csv, request.user.email)

                resp = {
                    'message': 'Mail sent'
                }

            else:
                resp = {
                    'message': 'No data to send'
                }

            return JsonResponse(resp)

        else:
            raise Http404()
