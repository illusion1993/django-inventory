"""Inventory App Forms"""
from datetime import datetime, timedelta

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from django.core.mail import EmailMessage
from inventory.message_constants import *

from inventory.models import User, Item, Provision

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


# Forms for inventory admins
class EditProfileForm(forms.ModelForm):
    """Form to update profile"""

    class Meta:
        """Meta Class"""
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone',
            'address',
            'id_number',
            'image'
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

        EmailMessage(
            subject=new_mail['subject'],
            body=new_mail['body'],
            to=recipients
        ).send()

        return super(AddItemForm, self).save(commit=True)

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

        EmailMessage(
            subject=new_mail['subject'],
            body=new_mail['body'],
            to=recipients
        ).send()

        return super(EditItemForm, self).save(commit=True)

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
    """Form to create new user"""

    def __init__(self, *args, **kwargs):
        super(ProvisionItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)
        self.fields['user'].queryset = self.fields[
            'user'].queryset.exclude(is_admin=True)

    def save(self, commit=True):
        """Send mail and save new provision object"""
        self.instance.approved = True
        self.instance.approved_on = datetime.now()
        self.instance.return_by = datetime.now() + timedelta(days=7)
        self.instance.quantity = 1

        # Decrementing item quantity
        item = Item.objects.get(id=self.instance.item.id)
        item.quantity -= self.instance.quantity
        item.save()

        # Sending mail
        new_mail = item_provision_mail(self.instance.item.name, self.instance.user.email)
        recipients = [str(self.instance.user.email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]

        EmailMessage(
            subject=new_mail['subject'],
            body=new_mail['body'],
            to=recipients,
            cc=cc_to
        ).send()

        return super(ProvisionItemForm, self).save(commit=True)

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
            'user',
            'return_by',
            'quantity'
        )
        widgets = {
            'user': autocomplete.ModelSelect2(url='user_autocomplete_ajax'),
            'item': autocomplete.ModelSelect2(url='item_autocomplete_ajax'),
        }


class ProvisionItemByRequestForm(forms.ModelForm):
    """Form to approve provision request"""

    def __init__(self, *args, **kwargs):
        super(ProvisionItemByRequestForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)

    def save(self, commit=True):
        """Save method marks a provision request approved, adds other info"""
        self.instance.approved = True
        self.instance.approved_on = datetime.now()
        self.instance.return_by = datetime.now() + timedelta(days=7)
        self.instance.quantity = 1

        # Decrementing item quantity
        item = Item.objects.get(id=self.instance.item.id)
        item_name = item.name
        item.quantity -= self.instance.quantity
        item.save()

        # Sending email
        user_email = self.instance.user.email
        new_mail = item_provision_mail(item_name, user_email)
        recipients = [str(self.instance.user.email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]

        EmailMessage(
            subject=new_mail['subject'],
            body=new_mail['body'],
            to=recipients,
            cc=cc_to
        ).send()

        return super(ProvisionItemByRequestForm, self).save(commit=True)

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
        )


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

    def save(self, commit=True):
        """Marking as returned, incrementing item quantity, sending mail"""
        self.instance.returned = True
        self.instance.returned_on = datetime.now()
        item = Item.objects.get(id=self.instance.item.id)
        item.quantity += self.instance.quantity
        item.save()

        # Sending mail now
        new_mail = item_returned_mail(self.instance.user.email)
        recipients = [str(User.objects.get(id=self.instance.user.id).email)]
        cc_to = [str(user.email) for user in User.objects.filter(is_admin=True)]

        EmailMessage(subject=new_mail['subject'], body=new_mail['body'], to=recipients, cc=cc_to).send()
        return super(ReturnItemForm, self).save(commit=True)


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