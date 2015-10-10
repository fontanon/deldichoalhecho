from django.contrib import admin

from ddah_file.models import DDAHFile


class DDAHFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(DDAHFile, DDAHFileAdmin)