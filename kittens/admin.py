from django.contrib import admin
from kittens import models

# Register your models here.
admin.site.register(models.Breed)
admin.site.register(models.Kitten)
admin.site.register(models.Rating)