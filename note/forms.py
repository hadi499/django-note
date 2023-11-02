from django import forms
from . models import Note, Category


class NoteForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Note
        fields = ('title', 'body', 'category')
