from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Note, Folder
import os
from django.conf import settings

def is_htmx_request(request):
    return request.headers.get('HX-Request') == 'true'

from django.db.models import Q

def index(request):
    q = request.GET.get('q', '').strip()
    if q:
        notes = Note.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).select_related('folder')
        context = {'folders': [], 'notes': notes, 'q': q}
    else:
        folders = Folder.objects.all()
        context = {'folders': folders, 'q': q}
    return render(request, 'notes/index.html', context)

def create_folder(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            folder = Folder.objects.create(name=name)
            return redirect('notes:folder_detail', pk=folder.pk)
    return redirect('notes:index')

def delete_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    if request.method == 'POST':
        if folder.notes.count() == 0:
            folder.delete()
        return redirect('notes:index')
    return HttpResponse('Invalid request', status=400)

def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    notes = folder.notes.all()
    context = {'folder': folder, 'notes': notes}
    if is_htmx_request(request):
        return render(request, 'notes/folder_detail.html', context)
    return render(request, 'notes/folder_detail.html', context)

def create_note(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        if title:
            note = Note.objects.create(title=title, content=content, folder=folder)
            if is_htmx_request(request):
                response = render(request, 'notes/partials/note_detail.html', {'note': note})
                response['HX-Push-Url'] = f'/note/{note.pk}/'
                return response
            return redirect('notes:view_note', pk=note.pk)
        return HttpResponse("Title is required", status=400)
    
    context = {'note': None, 'folder': folder}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_form.html', context)
    return render(request, 'notes/create_note.html', context)

def view_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    context = {'note': note}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_detail.html', context)
    return render(request, 'notes/view_note.html', context)

def edit_note(request, pk):
    import re
    import os
    from django.conf import settings
    
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        new_content = request.POST.get('content', '')
        if title:
            # --- Delete orphaned images from local disk ---
            old_img_urls = set(re.findall(r'<img[^>]+src="([^">]+)"', note.content))
            new_img_urls = set(re.findall(r'<img[^>]+src="([^">]+)"', new_content))
            
            deleted_img_urls = old_img_urls - new_img_urls
            for url in deleted_img_urls:
                if url.startswith(settings.MEDIA_URL):
                    filename = os.path.basename(url[len(settings.MEDIA_URL):])
                    file_path = os.path.join(settings.MEDIA_ROOT, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            # ----------------------------------------------
            
            note.title = title
            note.content = new_content
            note.save()
            if is_htmx_request(request):
                response = render(request, 'notes/partials/note_detail.html', {'note': note})
                response['HX-Push-Url'] = f'/note/{note.pk}/'
                return response
            return redirect('notes:view_note', pk=note.pk)
        return HttpResponse("Title is required", status=400)
    
    context = {'note': note}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_form.html', context)
    return render(request, 'notes/edit_note.html', context)

def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST' or request.method == 'DELETE':
        folder_pk = note.folder.pk if note.folder else None
        note.delete()
        if folder_pk:
            if is_htmx_request(request):
                response = HttpResponse('')
                response['HX-Redirect'] = f'/folder/{folder_pk}/'
                return response
            return redirect('notes:folder_detail', pk=folder_pk)
            
        if is_htmx_request(request):
            response = HttpResponse('')
            response['HX-Redirect'] = '/'
            return response
        return redirect('notes:index')
    return HttpResponse('Invalid request', status=400)

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        file_url = fs.url(filename)
        return JsonResponse({'url': file_url})
    return JsonResponse({'error': 'No image uploaded'}, status=400)

import json
def delete_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', '')
            if url and settings.MEDIA_URL in url:
                # Extract the filename regardless of http://localhost/... prefix
                media_idx = url.find(settings.MEDIA_URL)
                filename_part = url[media_idx + len(settings.MEDIA_URL):]
                filename = os.path.basename(filename_part)
                
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return JsonResponse({'status': 'success', 'message': 'File deleted'})
                else:
                    return JsonResponse({'status': 'success', 'message': 'File not found on disk'})
            else:
                return JsonResponse({'error': f'Invalid URL format: {url}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Exception: {str(e)}'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
