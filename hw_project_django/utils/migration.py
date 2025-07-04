import os
import django
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw_project.settings")
django.setup()

from quotes.models import Quote, Tag, Author  # noqa

mongo_uri = os.getenv("MONGODB_URI")
if not mongo_uri:
    raise ValueError("Missing MONGODB_URI in .env file")

client = MongoClient(mongo_uri)
db = client.hw

authors = db.authors.find()

for author in authors:
    Author.objects.get_or_create(
        fullname=author["fullname"],
        born_date=author["born_date"],
        born_location=author["born_location"],
        description=author["description"]
    )


for quote in db.quotes.find():
    if "author" not in quote:
        continue

    tags = []
    for tag in quote["tags"]:
        t, _ = Tag.objects.get_or_create(name=tag)
        tags.append(t)

    if not Quote.objects.filter(quote=quote["quote"]).exists():
        mongo_author = db.authors.find_one({"_id": quote["author"]})
        if not mongo_author:
            continue
        try:
            a = Author.objects.get(fullname=mongo_author["fullname"])
        except Author.DoesNotExist:
            continue

        q = Quote.objects.create(
            quote=quote["quote"],
            author=a
        )
        q.tags.add(*tags)