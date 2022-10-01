from django import forms


class SearchForm(forms.Form):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video')
    )
    search_query = forms.CharField()
    media_type = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=MEDIA_TYPES)
