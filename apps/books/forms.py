from django import forms
from .models import Books

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'author', 'isbn', 'category', 'publisher', 'published_at', 'total_copies']
        widgets = {
            'published_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['title'].required = True
        self.fields['author'].required = True
        self.fields['total_copies'].required = True
        # Optional fields
        self.fields['isbn'].required = False
        self.fields['category'].required = False
        self.fields['publisher'].required = False
        self.fields['published_at'].required = False

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip().title()
        return title

    def clean_author(self):
        author = self.cleaned_data.get('author')
        if author:
            author = author.strip().title()
        return author

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category:
            category = category.strip().title()
        return category

    def clean_publisher(self):
        publisher = self.cleaned_data.get('publisher')
        if publisher:
            publisher = publisher.strip().title()
        return publisher
