import requests
from bs4 import BeautifulSoup
from .models import Author, Quote, Tag

def scrape_and_save_quotes():
    url = "http://quotes.toscrape.com"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    quotes_divs = soup.find_all("div", class_="quote")

    for div in quotes_divs:
        text = div.find("span", class_="text").get_text(strip=True)
        author_name = div.find("small", class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in div.find_all("a", class_="tag")]

        author, _ = Author.objects.get_or_create(fullname=author_name)
        quote, created = Quote.objects.get_or_create(text=text, author=author)

        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            quote.tags.add(tag)

        quote.save()