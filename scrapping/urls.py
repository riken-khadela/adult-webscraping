from multiprocessing.spawn import import_main_path
from django.urls import path, include
from django.views.generic import View
from django.conf import Settings, settings
import os
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.conf.urls.static import static
from main.models import configuration
from main.views import *


def list_files(request):
    # Get the path to your STATIC_ROOT directory
    static_root = settings.MEDIA_ROOT

    # List all files in the directory
    files = os.listdir(static_root)

    # Create an HTML response with links to the files
    file_links = []
    for file in files:
        if file.endswith('.mp4') or file.endswith('.jpg') or 'video' in str(file):
            # file_path = os.path.join(static_root, file)
            file_links.append(f'<a href="/downloads/{file}/">{file}</a>')
        elif 'video' in str(file) and not file.endswith('.mp4') or not file.endswith('.jpg') and 'admin' not in str(file):
            file_links.append(f'<a href="/downloads/{file}/">{file}</a>')

    return HttpResponse("<br>".join(file_links))


def download_file(request, file_path):
    # Construct the full path to the file using the MEDIA_ROOT setting.
    media_root = settings.MEDIA_ROOT
    file = os.path.join(media_root, file_path)
    if os.path.basename(file).endswith('.csv'):file = os.path.join(os.getcwd(), file_path)
    # Check if the file exists.
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
            return response
    elif os.path.isdir(file):
        file_links = []
        files = os.listdir(file)
        if not files: return HttpResponse("Folder is empty",status=200)
        for file in files:
            if file.endswith('.mp4') or file.endswith('.jpg') or 'video' in str(file):
                # file_path = os.path.join(static_root, file)
                file_links.append(f'<a href="/downloads/{file}/">{file}</a>')
            elif 'video' in str(file) and not file.endswith('.mp4') or not file.endswith('.jpg') and 'admin' not in str(file):
                file_links.append(f'<a href="/downloads/{file}/">{file}</a>')
        return HttpResponse("<br>".join(file_links))
    else:
        HttpResponse("Folder not found.", status=404)


def csv_file(request, file_name):
    csv_root = settings.CSV_ROOT
    file_path = os.path.join(csv_root, file_name)
    
    if not os.path.exists(file_path):
        return HttpResponseNotFound("CSV file not found.")
    
    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    except PermissionError:
        raise PermissionDenied("Permission denied to access the CSV file.")

def return_csv_links(request):
    csv_root = settings.CSV_ROOT
    file_links = []

    for file_name in os.listdir(csv_root):
        if file_name.endswith('_details.csv'):
            file_links.append(f'<a href="/csv/{file_name}">{file_name}</a>')

    if not file_links:
        return HttpResponse("No CSV files found.")

    return HttpResponse("<br>".join(file_links))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('downloads/<path:file_path>/', download_file, name='download_file'),
    path('list_files/', list_files, name='list_file'),
    path('csv/<str:file_name>', csv_file, name='csv_file'),
    path('csv/', return_csv_links, name='csv_file_list'),
    path('', data_flair),
    path('API/', include('main.urls')),
    path('run-script',RunScript.as_view(),name='RunScript')

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)