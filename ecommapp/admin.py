from django.contrib import admin
from django.contrib.auth.models import Group,User
from .models import *



# unregistering Group and user
admin.site.unregister(Group)
admin.site.unregister(User)

# Register your models here.
admin.site.register(category)
admin.site.register(product_image)
admin.site.register(product)
