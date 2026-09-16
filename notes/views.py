from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Note
import os
from django.conf import settings

def is_htmx_request(request):
    return request.headers.get('HX-Request') == 'true'

def index(request):
    query = request.GET.get('q', '').strip()
    if query:
        notes = Note.objects.filter(title__icontains=query)
    else:
        notes = Note.objects.all()
        
    context = {'notes': notes}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_list.html', context)
    return render(request, 'notes/index.html', context)

def create_note(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        if title:
            note = Note.objects.create(title=title, content=content)
            response = render(request, 'notes/partials/note_detail.html', {'note': note})
            response['HX-Trigger'] = 'updateNoteList'
            response['HX-Push-Url'] = f'/note/{note.pk}/'
            return response
        # If title is empty, maybe return an error?
        return HttpResponse("Title is required", status=400)
    
    context = {'note': None}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_form.html', context)
    context['notes'] = Note.objects.all()
    return render(request, 'notes/create_note.html', context)

def view_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    context = {'note': note}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_detail.html', context)
    context['notes'] = Note.objects.all()
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
            response = render(request, 'notes/partials/note_detail.html', {'note': note})
            response['HX-Trigger'] = 'updateNoteList'
            response['HX-Push-Url'] = f'/note/{note.pk}/'
            return response
        return HttpResponse("Title is required", status=400)
    
    context = {'note': note}
    if is_htmx_request(request):
        return render(request, 'notes/partials/note_form.html', context)
    context['notes'] = Note.objects.all()
    return render(request, 'notes/edit_note.html', context)

def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST' or request.method == 'DELETE':
        note.delete()
        response = HttpResponse('''
            <div class="empty-state fade-in">
                <div class="empty-icon">📝</div>
                <h2>Select a note or create a new one</h2>
            </div>
        ''')
        response['HX-Trigger'] = 'updateNoteList'
        response['HX-Push-Url'] = '/'
        return response
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
