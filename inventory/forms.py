from datetime import timedelta
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils import timezone
from inventory.models import User, Item, Provision


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        #del self.fields['username']

    class Meta:
        model = User
        exclude = ()

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address', 'id_number', 'image']

class AddItemForm(forms.ModelForm):

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError("Please enter a valid quantity, only values larger than 0 allowed")

        return quantity

    class Meta:
        model = Item
        fields = ('name', 'description', 'returnable', 'quantity')

class EditItemForm(forms.ModelForm):

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity <= 0:
            raise forms.ValidationError("Please enter a valid quantity, only values larger than 0 allowed")

        return quantity

    class Meta:
        model = Item
        fields = ('description', 'quantity')

class ProvisionItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProvisionItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields['item'].queryset.exclude(quantity=0)
        self.fields['user'].queryset = self.fields['user'].queryset.exclude(is_admin=True)

    def save(self, commit=True):
        ins = super(ProvisionItemForm, self).save(commit=False)
        ins.approved = True
        ins.approved_on = timezone.now()
        ins.return_by = timezone.now() + timedelta(days=7)
        ins.quantity = 1

        # reducing remaining quantity of item issued
        item = Item.objects.get(id=self.cleaned_data['item'].id)
        item.quantity -= 1

        if commit:
            ins.save()
            item.save()

        return ins


    class Meta:
        model = Provision
        fields = ('item', 'user')

class ProvisionItemByRequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProvisionItemByRequestForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields['item'].queryset.exclude(quantity=0)

    def save(self, commit=True):
        ins = super(ProvisionItemByRequestForm, self).save(commit=False)
        ins.approved = True
        ins.approved_on = timezone.now()
        ins.return_by = timezone.now() + timedelta(days=7)
        ins.quantity = 1

        if commit:
            ins.save()

        return ins


    class Meta:
        model = Provision
        fields = ('item',)


class RequestItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs['initial']['user']
        super(RequestItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = self.fields['item'].queryset.exclude(quantity=0)

    def save(self, commit=True):
        ins = super(RequestItemForm, self).save(commit=False)
        ins.user = self.user
        if commit:
            ins.save()

        return ins

    class Meta:
        model = Provision
        fields = ('item',)
