"""Inventory App Models"""
import os
import time

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


# REGEX used
NAME_REGEX = RegexValidator(
    regex=r'^[a-zA-Z]+$',
    message="Please enter a valid name"
)

PHONE_REGEX = RegexValidator(
    regex=r'^\d{10,10}$',
    message="Please enter a valid phone number. Only 10 digits allowed."
)


class UserManager(BaseUserManager):
    """User Manager for custom User Model"""

    def _create_user(self, email, password, is_superuser, **extra_fields):
        """Save user in db"""

        if not email:
            raise ValueError('Email cannot be blank')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        """Create a user"""

        return self._create_user(
            email,
            password,
            False,
            **extra_fields
        )

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser"""

        return self._create_user(
            email,
            password,
            True,
            **extra_fields
        )


def get_image_path(instance, filename):
    """Generate a path for new image"""

    # Save extension of image
    extension = os.path.splitext(filename)[1]

    # Generate filename and path
    filename = str(int(round(time.time() * 1000))) + str(extension)
    return os.path.join(filename)


class User(AbstractBaseUser):
    """Custom user model"""

    email = models.EmailField(
        'email address',
        unique=True,
    )

    first_name = models.CharField(
        max_length=50,
        null=True,
        validators=[NAME_REGEX]
    )

    last_name = models.CharField(
        max_length=50,
        null=True,
        validators=[NAME_REGEX]
    )

    phone = models.CharField(
        validators=[PHONE_REGEX],
        max_length=15
    )

    address = models.TextField(
        null=True,
    )

    id_number = models.CharField(
        max_length=10,
        null=True,
        unique=True
    )

    image = models.ImageField(
        upload_to=get_image_path,
        blank=True,
        null=True
    )

    is_admin = models.BooleanField(
        default=False
    )

    is_superuser = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __unicode__(self):
        """unicode method"""
        return self.email

    @property
    def is_staff(self):
        """is staff method"""
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        """has permissions"""
        return True

    def has_module_perms(self, app_label):
        """has module permissions"""
        return True

    def get_short_name(self):
        """get short name"""
        return self.first_name

    def get_full_name(self):
        """get full name"""
        return self.first_name

    def delete_image(self):
        """delete profile image from file system"""
        try:
            os.remove(self.image.path)
        except:
            pass


class Item(models.Model):
    """Model for inventory items"""

    name = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    returnable = models.BooleanField()

    quantity = models.IntegerField(
        default=1,
    )

    def __unicode__(self):
        """unicode method"""
        return self.name


class Provision(models.Model):
    """Model for provision/issues"""

    item = models.ForeignKey(Item)
    user = models.ForeignKey(User)

    timestamp = models.DateTimeField(
        auto_now=True
    )

    approved = models.BooleanField(
        default=False
    )

    approved_on = models.DateTimeField(
        null=True,
    )

    return_by = models.DateTimeField(
        null=True,
    )

    quantity = models.IntegerField(
        null=True,
    )

    returned = models.BooleanField(
        default=False
    )

    returned_on = models.DateTimeField(
        null=True,
    )

    request_by_user = models.BooleanField(
        default=False
    )
