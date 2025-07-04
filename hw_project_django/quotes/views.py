from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quote, Author, Tag
from .forms import QuoteForm, AuthorForm
from django.db.models import Count
from .utils import scrape_and_save_quotes


def main(request, page=1):
    quotes = Quote.objects.all()
    paginator = Paginator(quotes,5)
    page_number = page
    quotes_on_page = paginator.get_page(page_number)

    top_tags = Tag.objects.annotate(num_quotes=Count("quote")).order_by("num_quotes")[:10]
    context = {
        "quotes": quotes_on_page,
        "has_prev": quotes_on_page.has_previous(),
        "has_next": quotes_on_page.has_next(),
        "prev_page": quotes_on_page.previous_page_number() if quotes_on_page.has_previous() else None,
        "next_page": quotes_on_page.next_page_number() if quotes_on_page.has_next() else None,
        "top_tags": top_tags,
    }

    return render(request, "quotes/index.html", context=context)

def tags_search(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    quotes = Quote.objects.filter(tags=tag)
    paginator = Paginator(quotes,5)
    page_number = request.GET.get("page", 1)
    quotes_on_page = paginator.get_page(page_number)

    context = {
        "quotes": quotes_on_page,
        "tag": tag,
        "has_prev": quotes_on_page.has_previous(),
        "has_next": quotes_on_page.has_next(),
        "prev_page": quotes_on_page.previous_page_number() if quotes_on_page.has_previous() else None,
        "next_page": quotes_on_page.next_page_number() if quotes_on_page.has_next() else None,

    }
    return render(request, "quotes/author_detail.html", context=context)

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, "quotes/author_detail.html", {"author": author})

@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = AuthorForm()
    return render(request, "quotes/add_author.html", {"form": form})

@login_required
def add_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = QuoteForm()
    return render(request, "quotes/add_quote.html", {"form": form})



@login_required
def scrape_view(request):
    if request.method == "POST":
        scrape_and_save_quotes()
        return redirect("quotes:list")
    return render(request, "quotes/scrape.html")