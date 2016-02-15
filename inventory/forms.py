"""Inventory App Forms"""
from datetime import datetime, timedelta

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.db import transaction
from django.forms.formsets import BaseFormSet
from inventory.message_constants import *

from inventory.models import User, Item, Provision
from inventory.signals import send_mail_signal

from datetimewidget.widgets import DateTimeWidget, DateWidget

from dal import autocomplete


# Forms for admin panel
class CustomUserCreationForm(UserCreationForm):
    """Form to create new user"""

    class Meta:
        """Meta Class"""
        model = User
        fields = (
            'email',
        )


class CustomUserChangeForm(UserChangeForm):
    """Form to edit a user from admin"""

    class Meta:
        """Meta Class"""
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone',
            'address',
            'id_number',
            'is_admin',
            'image',
        )


# Login Form
class LoginForm(forms.Form):
    """
    Login Form
    """

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


# Forms for inventory admins
class EditProfileForm(forms.ModelForm):
    """Form to update profile"""

    def clean_first_name(self):
        """Trim first name and make first letter uppercase"""
        return self.cleaned_data['first_name'].strip().title()

    def clean_last_name(self):
        """Trim Last name and make first letter uppercase"""
        return self.cleaned_data['last_name'].strip().title()

    def clean_id_number(self):
        """Trim id number"""
        return self.cleaned_data['id_number'].strip()

    class Meta:
        """Meta Class"""
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone',
            'address',
            'id_number',
        )


class AddItemForm(forms.ModelForm):
    """Form to add item"""

    def save(self, commit=True):
        """Sending mail and saving new item"""
        new_mail = item_added_mail(
            self.cleaned_data['name'],
            self.cleaned_data['quantity']
        )
        recipients = [str(user.email) for user in User.objects.all()]

        instance = super(AddItemForm, self).save(commit=True)
        send_mail_signal.send(sender=Item, mail_data=new_mail, recipients=recipients, cc_to=[])
        return instance

    def clean_name(self):
        """Trim item name"""
        return self.cleaned_data['name'].strip()

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError(
                "Please enter a valid quantity"
            )

        return quantity

    class Meta:
        """Meta Class"""
        model = Item
        fields = (
            'name',
            'description',
            'returnable',
            'quantity'
        )


class EditItemForm(forms.ModelForm):
    """Form to create edit item"""

    def save(self, commit=True):
        """Sending email and saving the item"""
        new_mail = item_edited_mail(self.instance.name)
        recipients = [str(user.email) for user in User.objects.filter(is_admin=True)]
        instance = super(EditItemForm, self).save(commit=True)
        send_mail_signal.send(sender=Item, mail_data=new_mail, recipients=recipients, cc_to=[])
        return instance

    def clean_name(self):
        """Trim item name"""
        return self.cleaned_data['name'].strip()

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError(
                "Please enter a valid quantity"
            )

        return quantity

    class Meta:
        """Meta Class"""
        model = Item
        fields = (
            'description',
            'quantity'
        )


class ProvisionItemForm(forms.ModelForm):
    """Form to Provision an item"""

    quantity = forms.IntegerField(required=False)
    return_by = forms.DateTimeField(
        required=False,
        widget=DateWidget(
            attrs={'class': "return-by"},
            usel10n=True,
            bootstrap_version=3,
            options={'format': 'dd/mm/yyyy'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(ProvisionItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)

        # self.fields['user'].queryset = self.fields[
        #     'user'].queryset.exclude(is_admin=True)

        self.empty_permitted = False

        self.fields['item'].widget.attrs['class'] = 'form-control'
        self.fields['user'].widget.attrs['class'] = 'form-control'
        self.fields['quantity'].widget.attrs['class'] = 'form-control'
        self.fields['return_by'].widget.attrs['class'] = 'form-control return-by'

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if 'item' in self.cleaned_data.keys():
            item = self.cleaned_data['item']
            q_max = item.quantity

            if not quantity:
                quantity = 1
                self.cleaned_data['quantity'] = quantity

            if quantity <= 0:
                raise forms.ValidationError(
                    "Please enter a valid quantity"
                )
            if quantity > q_max:
                raise forms.ValidationError(
                    "Only {0} items are available in inventory".format(q_max)
                )
        else:
            raise forms.ValidationError(
                "No item selected"
            )

        return quantity

    def clean_return_by(self):
        return_by = self.cleaned_data['return_by']

        if 'item' in self.cleaned_data.keys():
            item = self.cleaned_data['item']

            if not item.returnable:
                return None

            if not return_by:
                return_by = datetime.now() + timedelta(days=7)

            if return_by <= datetime.now():
                raise forms.ValidationError(
                    "Return by date should be in future"
                )

        else:
            raise forms.ValidationError(
                "No item selected"
            )

        return return_by

    @transaction.atomic
    def save(self, commit=True):
        """Send mail and save new provision object"""
        self.instance.approved = True
        self.instance.approved_on = datetime.now()

        # Decrementing item quantity
        item = Item.objects.get(id=self.instance.item.id)
        item.quantity -= self.instance.quantity
        item.save()

        instance = super(ProvisionItemForm, self).save(commit=True)

        # Sending mail
        new_mail = item_provision_mail(self.instance.item.name, self.instance.user.email)
        recipients = [str(self.instance.user.email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]
        send_mail_signal.send(sender=Provision, mail_data=new_mail, recipients=recipients, cc_to=cc_to)

        return instance

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
            'user',
            'quantity',
            'return_by'
        )
        widgets = {
            'user': autocomplete.ModelSelect2(url='user_autocomplete_ajax'),
            'item': autocomplete.ModelSelect2(url='item_autocomplete_ajax'),
        }


class ProvisionFormset(BaseFormSet):
    """Formset for provision items view"""

    def clean(self):
        """Creating clean function to check overall quantity of items in formset"""

        provisions = {}

        for form in self.forms:
            """From every form, extracting item and adding quantity"""
            if form.cleaned_data:
                item = form.cleaned_data['item']

                if item in provisions:
                    provisions[item] += form.cleaned_data['quantity']
                else:
                    provisions[item] = form.cleaned_data['quantity']

        for key in provisions.keys():
            """Now check if any item's requested quantity is more than available"""
            # print(type(key))
            if key.quantity < provisions[key]:
                self._non_form_errors.append(
                    'The available quantity for item {0} is only {1}'.format(
                        key,
                        key.quantity
                    )
                )


class ProvisionItemByRequestForm(forms.ModelForm):
    """Form to approve provision request"""

    quantity = forms.IntegerField(required=False)
    return_by = forms.DateTimeField(
        required=False,
        widget=DateWidget(
            attrs={'class': "return-by"},
            usel10n=True,
            bootstrap_version=3,
            options={'format': 'dd/mm/yyyy'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(ProvisionItemByRequestForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)

        self.fields['item'].widget.attrs['class'] = 'form-control'
        self.fields['quantity'].widget.attrs['class'] = 'form-control'
        self.fields['return_by'].widget.attrs['class'] = 'form-control return-by'

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if 'item' in self.cleaned_data.keys():
            item = self.cleaned_data['item']
            q_max = item.quantity

            if not quantity:
                quantity = 1
                self.cleaned_data['quantity'] = quantity

            if quantity <= 0:
                raise forms.ValidationError(
                    "Please enter a valid quantity"
                )
            if quantity > q_max:
                raise forms.ValidationError(
                    "Only {0} items are available in inventory".format(q_max)
                )
        else:
            raise forms.ValidationError(
                "No item selected"
            )

        return quantity

    def clean_return_by(self):
        return_by = self.cleaned_data['return_by']

        if 'item' in self.cleaned_data.keys():
            item = self.cleaned_data['item']

            if not item.returnable:
                return None

            if not return_by:
                return_by = datetime.now() + timedelta(days=7)

            if return_by <= datetime.now():
                raise forms.ValidationError(
                    "Return by date should be in future"
                )

        else:
            raise forms.ValidationError(
                "No item selected"
            )

        return return_by

    @transaction.atomic
    def save(self, commit=True):
        """Save method marks a provision request approved, adds other info"""
        self.instance.approved = True
        self.instance.approved_on = datetime.now()
        self.instance.request_by_user = True

        self.instance.return_by = datetime.now() + timedelta(days=7)
        self.instance.quantity = 1

        # Decrementing item quantity
        item = Item.objects.get(id=self.instance.item.id)
        item_name = item.name
        item.quantity -= self.instance.quantity
        item.save()
        instance = super(ProvisionItemByRequestForm, self).save(commit=True)

        # Sending email
        user_email = self.instance.user.email
        new_mail = item_provision_mail(item_name, user_email)
        recipients = [str(self.instance.user.email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]
        send_mail_signal.send(sender=Provision, mail_data=new_mail, recipients=recipients, cc_to=cc_to)

        return instance

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
            'quantity',
            'return_by'
        )
        widgets = {
            'item': autocomplete.ModelSelect2(url='item_autocomplete_ajax'),
        }


class RequestItemForm(forms.ModelForm):
    """Form to request an item"""

    def __init__(self, *args, **kwargs):
        super(RequestItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
        )


class ReturnItemForm(forms.ModelForm):
    """Form to return an item"""

    @transaction.atomic
    def save(self, commit=True):
        """Marking as returned, incrementing item quantity, sending mail"""
        self.instance.returned = True
        self.instance.returned_on = datetime.now()
        item = Item.objects.get(id=self.instance.item.id)
        item.quantity += self.instance.quantity
        item.save()
        instance = super(ReturnItemForm, self).save(commit=True)

        # Sending mail now
        new_mail = item_returned_mail(self.instance.user.email)
        recipients = [str(User.objects.get(id=self.instance.user.id).email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]
        send_mail_signal.send(sender=Provision, mail_data=new_mail, recipients=recipients, cc_to=cc_to)

        return instance

    class Meta:
        """Meta Class"""
        model = Provision
        fields = ()


class ImageUploadForm(forms.ModelForm):
    """Form to upload image via ajax"""

    class Meta:
        """Meta Class"""
        model = User
        fields = ('image',)


class DateFilterForm(forms.Form):
    """A form to display as filters on report page"""

    start_date = forms.DateTimeField(
        required=False,
        widget=DateWidget(
            attrs={'class': "filter-handle",
                   'id': "start-date-filter"},
            usel10n=True,
            bootstrap_version=3,
            options={
                'endDate': '"' + str(datetime.now().date()) + '"'
            }
        )
    )

    end_date = forms.DateTimeField(
        required=False,
        widget=DateWidget(
            attrs={'class': "filter-handle",
                   'id': "end-date-filter"},
            usel10n=True,
            bootstrap_version=3,
            options={
                'endDate': '"' + str((datetime.now() + timedelta(days=1)).date()) + '"'
            }
        )
    )
