from django import forms
from .models import Categories, category_options

class ListingForm(forms.Form):
    title = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea)
    bid = forms.IntegerField()
    image = forms.URLField(required=False)
    category = forms.CharField(required=False, widget=forms.SelectMultiple(choices=category_options))
