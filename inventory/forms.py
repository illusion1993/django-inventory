"""Inventory App Forms"""
from datetime import datetime, timedelta

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.mail import EmailMessage
from inventory.message_constants import item_added_mail, item_edited_mail

from inventory.models import User, Item, Provision

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
        recipients = []

        for user in User.objects.all():
            recipients.append(str(user.email))

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

        recipients = []

        for user in User.objects.filter(is_admin=True):
            recipients.append(str(user.email))

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

    class Meta:
        """Meta Class"""
        model = Provision
        fields = (
            'item',
            'user'
        )


class ProvisionItemByRequestForm(forms.ModelForm):
    """Form to approve provision request"""

    def __init__(self, *args, **kwargs):
        super(ProvisionItemByRequestForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields[
            'item'].queryset.exclude(quantity=0)

    def save(self, commit=True):
        """Save method marks a provision request approved, adds other info"""
        ins = super(ProvisionItemByRequestForm, self).save(commit=False)
        ins.approved = True
        ins.approved_on = datetime.now()
        ins.return_by = datetime.now() + timedelta(days=7)
        ins.quantity = 1

        if commit:
            ins.save()

        return ins

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
