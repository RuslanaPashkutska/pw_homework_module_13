from django import forms
from .models import Author, Quote, Tag

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]


class QuoteForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=250,
        help_text="Enter tags separated by commas (e.g. life, happiness, inspiration)"
    )

    class Meta:
        model = Quote
        fields = ["quote", "author", "tags"]

    def clean_tags(self):
        tags_str = self.cleaned_data["tags"]
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tags_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        tags_list = self.cleaned_data.get('tags', [])
        tag_objects = []
        for tag_name in tags_list:
            tag_obj, created = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag_obj)


        instance.tags.set(tag_objects)

        if commit:
            instance.save()
        return instance
