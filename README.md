
# PRE-ALPHA

## Do not use

# QueryPerms

Qperms is an authentication system for django that lets you use SQL queries as a
row-level permission system. This has a number of advantages over something like
django-gaurdian, the main one being that there's a single source of truth.
Normally with row-level permissions you need to explicitly set what users are
allowed to access an object, and keep that list up to date whenever the
situation changes. Keeping those permissions up to date when the situation
changes is generally done using signals, and is generally fragile. You're
essentially running code to make your permissions match your ideal state.

On the other hand QueryPerms derives your permissions implicitly.
For example if you were trying to make it so that a
shop owner can edit all the thumbnails for their product, you'd simply define a
permission like this `Q(product__shop__owner=user)`. This can involve a lot of
joins for more complicated permission relationships, but also means that you
don't ever have to run any code to keep your permissions up to date, which means
a lot less database writes when you make a change that affects a lot of rows.

It's built on top of django-threadlocals and django-rules.


## Basic example

```python3
from django.db import models
from django.contrib.sites.models import Site
from threadlocals.threadlocals import get_current_request
from django.contrib.sites.shortcuts import get_current_site
import qperms

class Shop(models.Model,qperms.AuthMixin):
    name=models.CharField(max_length=128)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ManyToManyField(Site)

    @classmethod
    def qperm_edit(cls):
        request=get_current_request()
        user=request.user
        site=get_current_site(request)
        return Q(owner=user) & Q(site=site)

class Product(models.Model,qperms.AuthMixin):
    name = models.CharField(max_length=128)
    shop = models.ForeignKey(Shop,
        on_delete=models.CASCADE,
        limit_choices_to=Shop.objects.perms("edit"))

    qperms_parent = "shop"

class ProductImage(models.Model,qperms.AuthMixin):
    product = models.ForeignKey(Product,
        on_delete=models.CASCADE,
        limit_choices_to=Product.objects.perms("edit"))
    image = models.ImageField(upload_to='product_media')

    qperms_parent = "product"

ProductImage.object.perms("edit") #Returns only objects attached to products
# where you own the shop
```

This here is a practical example, but QueryPerms easily supports much more
complicated permissions.

## Config

```python
INSTALLED_APPS+=[
    'rules',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'rules.permissions.ObjectPermissionBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware',
]
```
