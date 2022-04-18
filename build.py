#!/usr/bin/python3.9

import os
import json
from bs4 import BeautifulSoup
from markdown import markdown
from copy import deepcopy
from time import time

BUILD_DIR = "/home/ryan/python/staticsitegenerator/"
ROOT_DIR = "www/"
BLOG_DIR = ROOT_DIR + "blog/"
METADATA = "/article.json"
MOTD = "motd.html"
TEMPLATE = "template.html"
INDEX = "index.html"
CONTENT_SRC = "/article.md"
CONTENT_OUT = "/article.html"

def timer(func):
    '''Print millisecond running-time information for decorated function to stdout'''
    def inner(*args, **kwargs):
        print(f"[...]{' '*6}-.---ms : Entering {func.__name__:>40}")
        started = time()
        ret = func(*args, **kwargs)
        finished = time()
        elapsed = 1000 * (finished - started)
        print(f"[ = ] {elapsed:>10.3f}ms : Exiting {func.__name__:>41}")
        return ret
    return inner

@timer
def make_soup(html: str) -> BeautifulSoup:
    '''Convenience alias for BeautifulSoup(str, 'html.parser')'''
    return BeautifulSoup(html, 'html.parser')

@timer
def get_page_folder_names() -> list[str]:
    '''Returns a list of strings containing the names of all folders in BLOG_DIR'''
    return os.listdir(BLOG_DIR)

def get_metadata(page_name: str):
    '''Parses page metadata json into Python object (usually Dict)'''
    with open(BLOG_DIR + page_name + METADATA) as f:
        return json.load(f)

@timer
def get_template() -> BeautifulSoup:
    with open(ROOT_DIR + TEMPLATE, 'r') as f:
        return make_soup(f.read())

@timer
def get_content(page_name: str) -> str:
    '''Parse page's Markdown content into a BeautifulSoup object'''
    with open(BLOG_DIR + page_name + CONTENT_SRC, 'r') as f:
        return make_soup(markdown(f.read()))

@timer
def get_motd() -> BeautifulSoup:
    '''Parses and returns the MOTD as a BeautifulSoup object'''
    with open(ROOT_DIR + MOTD, 'r') as f:
        return make_soup(f.read())

@timer
def get_article_links(for_homepage=False):
    '''Generates BeautifulSoup object containing links for insertion
    into div type="nav"'''
    soup = BeautifulSoup()
    for page in get_page_folder_names():
        # Extract info from metadata for this page
        metadata = get_metadata(page)
        url = metadata['url']
        name = metadata['name']

        # Create new div, a tags
        new_div = soup.new_tag("div")
        new_div['class'] = "nav-item"

        # Bullet link
        new_ul = soup.new_tag("ul")
        new_li = soup.new_tag("li")
        new_ul.append(new_li)

        if for_homepage == True:
            # Modify link hrefs for homepage
            new_a = soup.new_tag("a", href=f"blog/{url}/article.html")
        else:
            new_a = soup.new_tag("a", href=f"../{url}/article.html")
            
        new_a.string = name

        # Append new tags
        new_li.append(new_a)
        new_ul.append(new_li)
        new_div.append(new_ul)
        soup.append(new_div)

    return soup

@timer
def enforce_article_folder_names() -> None:
    '''Renames article folders if they mismatch their article.json'''
    for folder_name in get_page_folder_names():
        url = get_metadata(folder_name)['url']
        if url != folder_name:
            os.rename(BLOG_DIR + folder_name, BLOG_DIR + url)

@timer
def build_articles() -> None:
    '''Generates static webpages for each article in www/blog'''

    # Parse page template HTML once:
    template = get_template()

    # Read MOTD once:
    motd = get_motd()

    # Generate article links BeautifulSoup object once:
    nav_links = get_article_links()

    # Get list of string folder names in www/blog
    pages: list[str] = get_page_folder_names()

    # For each page
    for page in pages:

        # Make a copy of template to modify
        soup = deepcopy(template)

        # Parse article.json into dict
        metadata: dict = get_metadata(page)
        name = metadata['name']
        #url = metadata['url']
        #date_published = metadata['date-published']

        # Write page title to div class="page-title" in italics
        new_i = soup.new_tag("i")
        new_i.string = name
        soup.find("div", "page-title").append(new_i)

        # Append MOTD to div class="alert"
        soup.find("div", "alert").append(deepcopy(motd))

        # Parse and write article.md into div class="article"
        soup.find("div", "article").append(get_content(page))

        # Append generated nav-items to nav div
        soup.find("div", "nav").append(deepcopy(nav_links))

        # Write modified template to respective directory
        with open(BLOG_DIR + page + CONTENT_OUT, 'w') as f:
            f.write(str(soup))

@timer
def build_homepage() -> None:
    '''Generates a static home page'''
    soup = get_template()
    motd = get_motd()
    nav_links = get_article_links(for_homepage=True)

    # Fix icon image src and link href
    icon = soup.find("div", "icon")
    icon.a['href'] = "index.html"
    icon.img['src'] = "res/me96.gif"

    # Write motd
    soup.find("div", "alert").append(motd)

    # Write page title
    new_i = soup.new_tag("i")
    new_i.string = "Ryan's wicked sick technoblog (name pending)"
    soup.find("div", "page-title").append(new_i)

    # Parse and write article.md into div class="article"
    with open(ROOT_DIR + "index.md", 'r') as f:
        content = make_soup(markdown(f.read()))
    soup.find("div", "article").append(content)

    # Append generated nav-items to nav div
    soup.find("div", "nav").append(nav_links)

    # Write modified template to ROOT_DIR as index.html
    with open(ROOT_DIR + INDEX, 'w') as f:
        f.write(str(soup))

@timer
def build():
    os.chdir(BUILD_DIR)
    build_articles()
    build_homepage()
    enforce_article_folder_names()

if __name__ == '__main__':
    try:
        print(f"Building...")
        build()
        print(f"Build completed!")
    except(Exception) as e:
        print(e)
        print(f"Build failed.")