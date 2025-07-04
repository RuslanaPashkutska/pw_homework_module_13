from django import template
from quotes.models import Author

register = template.Library()

@register.filter(name="author")
def get_author(author_id):
    try:
        author = Author.objects.get(id=author_id)
        return author.fullname
    except Author.DoesNotExist:
        return "Unknown"