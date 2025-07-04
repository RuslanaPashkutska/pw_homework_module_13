import os
import sys
import django
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw_project.settings")

django.setup()

from quotes.models import Author, Quote, Tag

def migrate_quotes(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as fd:
        quotes = json.load(fd)

    for quote in quotes:
        author_name = quote.get("author")
        quote_text = quote.get("quote")
        tags_list = quote.get("tags", [])

        author, _ = Author.objects.get_or_create(fullname=author_name)

        quote, created = Quote.objects.get_or_create(quote=quote_text, author=author)

        tag_objects = []
        for tag_name in tags_list:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)
        quote.tags.set(tag_objects)

        quote.save()

    print("Migración completada con éxito.")

if __name__ == "__main__":
    migrate_quotes("utils/quotes.json")