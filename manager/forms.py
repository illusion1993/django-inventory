from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django import forms

from manager.models import User, Item, Provision


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)

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

class AddItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('name', 'description', 'returnable', 'quantity')

class EditItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('description', 'quantity')

class ProvisionItemForm(forms.ModelForm):

    class Meta:
        model = Provision
        fields = ('item', 'user')

class RequestItemForm(forms.ModelForm):

    class Meta:
        model = Provision
        fields = ('item',)

class ReturnItemForm(forms.ModelForm):

    class Meta:
        model = Provision
        fields = ()

