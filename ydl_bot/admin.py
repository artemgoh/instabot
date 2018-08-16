from django.contrib import admin

from . import models


admin.site.register(models.InstPost)
admin.site.register(models.LikeQty)
admin.site.register(models.Description)

# Register your models here.
