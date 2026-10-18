import re
from datetime import date
from urllib.parse import urljoin, urlparse

import click
import requests
from bs4 import BeautifulSoup

TOP_WORDS_COUNT = 10

CURRENT_YEAR = date.today().year
YEAR_SUFFIXES = [str(year) for year in range(CURRENT_YEAR - 3, CURRENT_YEAR + 1)]
COMMON_SUFFIXES = ['01', '123', '1!', '2!', '3!', '1', '2', '3', '0', '00']


def get_html_of(url):
    """Download the HTML content of the given URL as a string."""
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise click.ClickException(
            f'HTTP status code {response.status_code} returned, but 200 was expected.'
        )
    return response.content.decode(response.encoding or 'utf-8', errors='replace')


def get_all_words_from(url):
    """Return every word found in the text of the webpage at url."""
    soup = BeautifulSoup(get_html_of(url), 'html.parser')
    return re.findall(r'\w+', soup.get_text())


def count_occurrences_in(word_list):
    """Return a dict mapping each word to its occurrence count."""
    word_count = {}
    for word in word_list:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count


def get_top_words(word_list, limit=TOP_WORDS_COUNT):
    """Return the `limit` most frequent (word, count) pairs."""
    word_count = count_occurrences_in(word_list)
    return sorted(word_count.items(), key=lambda item: item[1], reverse=True)[:limit]


def get_links_from(url):
    """Return all same-domain absolute URLs linked from the page at url."""
    base_domain = urlparse(url).netloc
    soup = BeautifulSoup(get_html_of(url), 'html.parser')
    links = set()
    for tag in soup.find_all('a', href=True):
        absolute = urljoin(url, tag['href'])
        if urlparse(absolute).netloc == base_domain:
            links.add(absolute.split('#')[0])
    return links


def crawl(start_url, depth):
    """Breadth-first crawl collecting all words up to `depth` levels deep."""
    visited = set()
    all_words = []
    current_level = {start_url}
    for _ in range(depth + 1):
        next_level = set()
        for url in current_level:
            if url in visited:
                continue
            visited.add(url)
            all_words.extend(get_all_words_from(url))
            next_level.update(get_links_from(url))
        current_level = next_level
    return all_words


def mutate(word):
    """Return common password mutations of a single word.

    Applies case variants (original, lower, upper, capitalized) and appends
    common suffixes such as recent years, digits and symbols.
    """
    variants = {word, word.lower(), word.upper(), word.capitalize()}
    suffixes = YEAR_SUFFIXES + COMMON_SUFFIXES
    for variant in tuple(variants):
        for suffix in suffixes:
            variants.add(variant + suffix)
    return variants


@click.command()
@click.option('--url', '-u', required=True, help='URL of the webpage to extract from.')
@click.option('--length', '-l', default=0, show_default=True,
              help='Minimum word length (0 disables the filter).')
@click.option('--output', '-o', default=None,
              help='Write the wordlist to this file instead of stdout.')
@click.option('--depth', '-d', default=0, show_default=True,
              help='Crawl depth, following same-domain links only.')
def main(url, length, output, depth):
    """Extract words from a webpage and build a password wordlist."""
    all_words = crawl(url, depth)

    top_words = get_top_words(all_words)
    click.echo(f'Top {min(TOP_WORDS_COUNT, len(top_words))} words:')
    for word, count in top_words:
        click.echo(f'  {word}: {count}')

    wordlist = set()
    for word in all_words:
        if length and len(word) < length:
            continue
        wordlist.update(mutate(word))

    if output:
        with open(output, 'w', encoding='utf-8') as writer:
            for word in sorted(wordlist):
                writer.write(word + '\n')
        click.echo(f'Wrote {len(wordlist)} words to {output}')
    else:
        click.echo(f'\nGenerated wordlist ({len(wordlist)} words):')
        for word in sorted(wordlist):
            click.echo(word)


if __name__ == '__main__':
    main()
