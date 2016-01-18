import os
from time import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.

class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_superuser, **extra_fields):

        if not email:
            raise ValueError('Email cannot be blank')

        email = self.normalize_email(email)

        user = self.model(email = email, is_superuser = is_superuser, **extra_fields)

        user.set_password(password)
        user.save(self._db)
        return user

    def create_user(self, email, password, **extra_fields):

        return self._create_user(email, password,
                                 False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        return self._create_user(email, password,
                                 True, **extra_fields)

def get_image_path(instance, filename):
    return os.path.join('media', str(instance.email), filename)

class User(AbstractBaseUser):

    email = models.EmailField('email address', unique=True, null=False, blank=False)

    regex = RegexValidator(regex=r'^[a-zA-Z]+$', message="Please enter a valid name")
    first_name = models.CharField(max_length=50, default=None, null=True, validators=[regex])
    last_name = models.CharField(max_length=50, default=None, null=True, validators=[regex])

    regex = RegexValidator(regex=r'^\d{10,10}$', message="Please enter a valid phone number. Only 10 digits allowed.")
    phone = models.CharField(validators=[regex], max_length=15)

    address = models.TextField(null=True, default=None)
    id_number = models.CharField(max_length=10, null=True, default=None, unique=True)

    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    #image = models.CharField(max_length=100, default=None, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __unicode__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_short_name(self):
        return self.first_name



class Item(models.Model):

    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    returnable = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1, blank=False, null=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('items_list')

class Provision(models.Model):

    item = models.ForeignKey(Item)  #add on_delete attribute
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)

    approved = models.BooleanField(default=False)
    approved_on = models.DateTimeField(default=None, null=True, blank=True)
    return_by = models.DateTimeField(default=None, null=True, blank=True)
    quantity = models.IntegerField(default=None, null=True, blank=True)

    returned = models.BooleanField(default=False)
    returned_on = models.DateTimeField(default=None, null=True, blank=True)

    def __unicode__(self):
        return self.user.email

    def get_absolute_url(self):
        return reverse('provision_by_request', kwargs={'pk':self.id})