from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Note, Category
from django.db.models import Q
from .forms import NoteForm


def home(request):

    if 'q' in request.GET:
        q = request.GET['q']
        result = Q(title__icontains=q)
        notes = Note.objects.filter(result)
    else:
        notes = Note.objects.all().order_by('-id')

    categories = Category.objects.all()
    context = {
        'notes': notes,
        'categories': categories

    }
    return render(request, 'home.html', context)


def detail(request, pk):
    categories = Category.objects.all()
    notes = Note.objects.all()
    note = get_object_or_404(Note, id=pk)
    context = {
        'notes': notes,
        'categories': categories,
        'note': note,
    }
    return render(request, 'detail.html', context)


def createNote(request):
    categories = Category.objects.all()
    form = NoteForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid:
            form.save()
            return redirect('home')
    return render(request, 'create.html', {'form': form, 'categories': categories})


def category_view(request, pk=None):
    # Menggunakan slug sebagai parameter untuk mengambil kategori yang sesuai
    category = get_object_or_404(Category, id=pk)

    if 'q' in request.GET:
        q = request.GET['q']
        result = Q(title__icontains=q)
        notes = Note.objects.filter(result)
    else:
        notes = category.note_set.all()

    context = {

        # 'note_categories': category.note_set.all(),
        'categories': Category.objects.all(),
        # 'notes': Note.objects.all()
        'notes': notes
    }

    return render(request, 'category.html', context)


def category_view_detail(request, pk):
    # Menggunakan slug sebagai parameter untuk mengambil kategori yang sesuai
    category = get_object_or_404(Category, id=pk)

    context = {
        'note': note
    }

    return render(request, 'category_detail.html', context)


def deleteNote(request, pk):
    if request.method == 'POST':
        post = Note.objects.get(pk=pk)
        post.delete()
    return redirect('home')


def updateNote(request, pk):
    categories = Category.objects.all()
    note = Note.objects.get(id=pk)
    data = {
        'title': note.title,
        'body': note.body,
        'category': note.category

    }
    form = NoteForm(request.POST or None,
                    initial=data, instance=note)
    if request.method == 'POST':
        if form.is_valid:
            form.save()
            return redirect('home')
    return render(request, 'update.html', {'form': form, 'categories': categories})
