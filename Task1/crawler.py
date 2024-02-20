from url import get_url
from nltk.stem import WordNetLemmatizer
import numpy as np
import os as o
from tkinter import ttk
import tkinter as tk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk import pos_tag
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

# Define the URL
url = "https://pureportal.coventry.ac.uk/en/organisations/ihw-centre-for-health-and-life-sciences-chls/"

# Call the function and save the result into the url variable
new_url = get_url(url)
response = requests.get(new_url)


def create_csv():
    """
    Creates a new CSV file with specified headers.

    Returns:
    tuple: A tuple containing the CSV file object and the CSV writer object.
    """
    print("Creating CSV file...")
    try:
        csv_file = open("data.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(csv_file)
        writer.writerow(["Title", "Authors", "Publication Year",
                        "Publication Link", "Authors Profile"])
        print("CSV file created successfully.")
        return csv_file, writer
    except Exception as e:
        print("Error creating CSV file:", str(e))
        return None, None


def update_csv():
    """
    Reads the existing CSV file and returns its contents as a pandas DataFrame.

    Returns:
    DataFrame: The contents of the existing CSV file as a DataFrame.
    """
    current_data = pd.read_csv("data.csv", index_col="Unnamed: 0")
    return current_data


def crawl_data(response, writer):
    """
    Scrapes data from the provided webpage response and writes it to the CSV file using the provided CSV writer.

    Args:
    response (Response): The response object obtained from making a request to the webpage.
    writer (csv.writer): The CSV writer object.

    Returns:
    None
    """
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        publication_elements = soup.find_all("div", class_="result-container")
        for publication in publication_elements:
            title_element = publication.find("h3", class_="title")
            title = title_element.get_text(strip=True)

            authors_elements = publication.find_all(
                "a", attrs={"rel": "Person"})
            authors = [author.get_text(strip=True)
                       for author in authors_elements]
            publication_year_element = publication.find("span", class_="date")
            publication_year = publication_year_element.get_text(
                strip=True) if publication_year_element else ""

            publication_link_element = publication.find("a", class_="link")
            publication_link = publication_link_element["href"] if publication_link_element else ""

            authors_profile_element = publication.find(
                "a", attrs={"rel": "Person"})
            authors_profile = authors_profile_element["href"] if authors_profile_element else ""

            writer.writerow(
                [title, ",".join(authors), publication_year, publication_link, authors_profile])

        print("CSV file is updated successfully.")

    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)


def crawl_main():
    """
    Main function for crawling and updating the CSV file with scraped data.

    Returns:
    None
    """
    # Fetch the webpage
    new_url = get_url(url)  # You need to define new_url
    print(new_url)
    response = requests.get(new_url)
    print(response)

    # Create the CSV file and get the writer object
    csv_file, writer = create_csv()

    # Update the CSV file with scraped publications
    crawl_data(response, writer)

    # Close the CSV file
    csv_file.close()


if __name__ == "__main__":
    crawl_main()
