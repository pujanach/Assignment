from crawler import create_csv  # Import the create_csv function directly
from crawler import crawl_main

from search import search_query
from UI import ui_main
from url import get_url


def main():

    # Call the necessary functions
    crawl_main()
    search_query()
    ui_main()


if __name__ == "__main__":
    main()
