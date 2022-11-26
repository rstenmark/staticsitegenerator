#!/usr/bin/python3.11
from _paths import *
from shutil import rmtree
import os
import argparse

# Define parser
parser = argparse.ArgumentParser(
    prog='Article creation utility',
    description='This script assists in the creation of new article folders.'
)
parser.add_argument(
    'article_name',
    type=str,
    nargs=1,
    help='This is the published name of the article.'
)
parser.add_argument(
    'url',
    type=str,
    nargs=1,
    help="""This is the name of the folder containing the article. \
        This string must contain only URL-safe and ext4-safe characters, additionally
        excluding special characters and sequences (Ex: .., ~, /, \)"""
)
parser.add_argument(
    'publish_date',
    type=str,
    nargs=1,
    help='This is the publication date of the article using format: mm-dd-yy. (Ex: July 14th 2022 -> 07-14-22)'
)
parser.add_argument(
    '-f',
    '--force',
    required=False,
    default=False,
    action='store_true',
    help='Delete and overwrite any pre-existent article at url'
)
parser.add_argument(
    '-v',
    '--verbose',
    required=False,
    default=False,
    action='store_true',
    help='Enable verbose status output'
)

# Parse arguments
args = parser.parse_args()

def create_article(name: str, url: str, publish_date: str, force=False, verbose=False, dir=BUILD_DIR+BLOG_DIR) -> str:
    '''Creates a new article in www/blog with the given name and URL, optionally
    overwriting an extant article at www/blog/{url}'''
    
    # Construct an absolute path to the article folder
    article_path: str = dir + url + "/"
    if verbose: print(f"Creating article named {name} at {article_path}")

    # Check if article is extant
    if url in os.listdir(dir):
        # Article already exists, so delete it or complain to caller about it
        if verbose: print(f"An article with the URL {url} already exists.")
        if force == True:
            if verbose: print(f"Deleting {url}")
            rmtree(article_path)
        else:
            if verbose: print(f"Article creation utility cannot continue execution.")
            raise RuntimeError(f"An article with the URL {url} already exists. (use -f flag to overwrite)")
    
    # Article does not exist, create it
    if verbose: print(f"Creating directory: {article_path}")
    os.mkdir(article_path)
    if verbose: print(f"Creating directory: {article_path + 'res'}")
    os.mkdir(article_path + 'res')
    if verbose: print(f"Creating article.json")
    with open(article_path + 'article.json', 'w') as f:
        f.write(
f"""{{
    "name": "{name}",
    "url": "{url}",
    "date": "{publish_date}"
}}"""
        )
    if verbose: print(f"Creating article.md")
    with open(article_path + 'article.md', 'w') as f:
        f.write("")

    if verbose: print(f"Article {name} was created successfully!")
    return article_path

create_article(
    args.article_name[0],
    args.url[0],
    args.publish_date[0],
    args.force,
    args.verbose
)