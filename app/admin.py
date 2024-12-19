from django.contrib import admin
from .models import VideosData, send_mail, sender_mail, configuration, cetegory, RunScript
import logging
logger = logging.getLogger(__name__)

admin.site.register(send_mail)
admin.site.register(sender_mail)
# admin.site.register(cetegory)

from django.contrib import admin
from .models import VideosData

from django.urls import path
import shutil
from django.http import JsonResponse

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        try:
            # Retrieve disk space info
            total, used, free = shutil.disk_usage("/")
            disk_info = {
                "total": f"{total // (2**30)} GB",
                "used": f"{used // (2**30)} GB",
                "free": f"{free // (2**30)} GB",
            }
        except Exception as e:
            disk_info = {
                "total": "N/A",
                "used": "N/A",
                "free": "N/A",
                "error": str(e),
            }

        # Log disk_info for debugging
        logger.info(f"Disk Info: {disk_info}")

        # Add to context
        extra_context = extra_context or {}
        extra_context['disk_info'] = disk_info
        return super().index(request, extra_context=extra_context)

admin_site = CustomAdminSite(name="custom_admin")

@admin.register(VideosData)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('Video_name', 'deleted_or_not', 'created_at', 'Username', 'video', 'image')  # Include created_at here
    list_filter = ('created_at',)  # Optional: Add filter for created_at
    search_fields = ('Username', 'video')  # Optional: Add search fields

@admin.register(configuration)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('website_name','lastime_able_to_login_or_not', 'username', 'password')
    search_fields = ('lastime_able_to_login_or_not','website_name')
    
@admin.register(cetegory)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('category','link')
    
@admin.register(RunScript)
class VideosDataAdmin(admin.ModelAdmin):
    list_display = ('datetime',)


