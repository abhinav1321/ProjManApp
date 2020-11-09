from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.ExtendedUser)
admin.site.register(models.Board)
admin.site.register(models.List)
admin.site.register(models.Team)
admin.site.register(models.Card)
admin.site.register(models.FileUpload)
admin.site.register(models.TeamMembers)
admin.site.register(models.CardChecklist)
