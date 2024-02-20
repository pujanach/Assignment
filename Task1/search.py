import string
import numpy as np
import pandas as pd
import nltk
import json
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag
from bs4 import BeautifulSoup
from tkinter import ttk
import tkinter as tk
import requests
import os

nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

# Global variables
stop_words = stopwords.words("english")
lemmatizer = WordNetLemmatizer()
indexes = {}


# Read data from CSV
def read_data():
    """
    Reads data from the CSV file and returns it as a pandas DataFrame.

    Returns:
    DataFrame: The data read from the CSV file.
    """
    df = pd.read_csv('data.csv').reset_index().rename(columns={'index': 'SN'})
    return df


# Text preprocessing function
def preprocess_text(txt):
    """
    Preprocesses the input text.

    Args:
    txt (str): The input text to be preprocessed.

    Returns:
    str: The preprocessed text.
    """
    txt = txt.lower()  # Make lowercase
    # Remove punctuation marks
    txt = txt.translate(str.maketrans('', '', string.punctuation))
    txt = lemmatize(txt)
    return txt


# Part-of-speech tagging and lemmatization
def lemmatize(text):
    """
    Lemmatizes the input text.

    Args:
    text (str): The input text to be lemmatized.

    Returns:
    str: The lemmatized text.
    """
    tokens = nltk.word_tokenize(text)
    processed_text = ""
    for token in tokens:
        if token not in stop_words:
            processed_text += lemmatizer.lemmatize(
                token, get_wordnet_pos(token)) + " "
    return processed_text.strip()


# Map POS tag to first character lemmatize() accepts
def get_wordnet_pos(word):
    """
    Maps POS tags to WordNet POS tags.

    Args:
    word (str): The word to get the POS tag for.

    Returns:
    str: The WordNet POS tag corresponding to the input word.
    """
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


# Preprocess dataframe
def preprocess_df(df):
    """
    Preprocesses the DataFrame.

    Args:
    df (DataFrame): The input DataFrame to be preprocessed.

    Returns:
    DataFrame: The preprocessed DataFrame.
    """
    df['Title'] = df['Title'].apply(preprocess_text)
    df['Author'] = df['Authors'].str.lower()
    print(df.columns)
    df = df.drop(columns=['Author', 'Publication Year'], axis=1)
    return df


# Indexer Function
def apply_index(inputs, index):
    """
    Applies indexing to the input data.

    Args:
    inputs (dict): The input data to be indexed.
    index (dict): The index dictionary.

    Returns:
    dict: The updated index dictionary.
    """
    words = inputs['Title'].split()
    SN = int(inputs['SN'])
    for word in words:
        if word in index.keys():
            if SN not in index[word]:
                index[word].append(SN)
        else:
            index[word] = [SN]
    return index


# Build full index
def full_index(df, index):
    """
    Builds the full index.

    Args:
    df (DataFrame): The DataFrame containing the data.
    index (dict): The index dictionary.

    Returns:
    dict: The updated index dictionary.
    """
    for i in range(len(df)):
        inp = df.loc[i, :]
        ind = apply_index(inputs=inp, index=index)
    return ind


# Construct index
def construct_index(df, index):
    """
    Constructs the index.

    Args:
    df (DataFrame): The DataFrame containing the data.
    index (dict): The index dictionary.

    Returns:
    dict: The constructed index.
    """
    queue = preprocess_df(df)
    ind = full_index(df=queue, index=index)
    return ind


# Save index to JSON file
def save_index_to_json(index, filename):
    """
    Saves the index to a JSON file.

    Args:
    index (dict): The index dictionary.
    filename (str): The filename to save the index to.

    Returns:
    None
    """
    with open(filename, 'w') as new_file:
        json.dump(index, new_file, sort_keys=True, indent=4)


# Load index from JSON file
def load_index_from_json(filename):
    """
    Loads the index from a JSON file.

    Args:
    filename (str): The filename to load the index from.

    Returns:
    dict: The loaded index.
    """
    with open(filename, 'r') as file:
        loaded_index = json.load(file)
    return loaded_index


# Index data
def index_data(df, indexes):
    """
    Indexes the data.

    Args:
    df (DataFrame): The DataFrame containing the data.
    indexes (dict): The index dictionary.

    Returns:
    dict: The indexed data.
    """
    constructed_index = construct_index(df=df, index=indexes)
    return constructed_index


# Demonstrate query processing
def demonstrate_query_processing():
    """
    Demonstrates query processing.

    Returns:
    str: The processed search query.
    """
    sample = input('Enter Search Terms: ')
    processed_query = preprocess_text(sample)
    print(f'Processed Search Query: {processed_query}')
    return processed_query


# Split query terms
def split_query(terms):
    each = preprocess_text(terms)
    return each.split()


# Union operation
def union(lists):
    """
    Performs the union operation.

    Args:
    lists (list): The lists to perform the union operation on.

    Returns:
    list: The result of the union operation.
    """
    union_list = list(set.union(*map(set, lists)))
    union_list.sort()
    return union_list


# Intersection operation
def intersection(lists):
    """
    Performs the intersection operation.

    Args:
    lists (list): The lists to perform the intersection operation on.

    Returns:
    list: The result of the intersection operation.
    """
    intersect_list = list(set.intersection(*map(set, lists)))
    intersect_list.sort()
    return intersect_list


# Vertical search engine
def vertical_search_engine(df, query, index):
    """
    Performs vertical search engine.

    Args:
    df (DataFrame): The DataFrame containing the data.
    query (str): The search query.
    index (dict): The index dictionary.

    Returns:
    DataFrame or str: The search result DataFrame or a message if no result is found.
    """
    query_split = split_query(query)
    retrieved = []
    for word in query_split:
        if word in index.keys():
            retrieved.append(index[word])

    # Ranked Retrieval
    if len(retrieved) > 0:
        high_rank_result = intersection(retrieved)
        low_rank_result = union(retrieved)
        c = [x for x in low_rank_result if x not in high_rank_result]
        high_rank_result.extend(c)
        result = high_rank_result

        final_output = df[df['SN'].isin(result)].reset_index(drop=True)

        # Return result in order of Intersection ----> Union
        dummy = pd.Series(result, name='SN').to_frame()
        result = pd.merge(dummy, final_output, on='SN', how='left')

    else:
        result = 'No result found'

    return result


# Test search engine
def test_search_engine(df, indexed):
    """
    Tests the search engine.

    Args:
    df (DataFrame): The DataFrame containing the data.
    indexed (dict): The indexed data.

    Returns:
    DataFrame or str: The search result DataFrame or a message if no result is found.
    """
    query = input("Enter your search query: ")
    return vertical_search_engine(df, query, indexed)


def fun(path):
    """
    Function to format URLs as links.

    Args:
    path (str): The URL path.

    Returns:
    str: The formatted URL as a link.
    """
    if pd.notnull(path):
        # returns the final component of a url
        f_url = path.split('/')[-1]
        # convert the url into link
        return '<a href="{}">{}</a>'.format(path, f_url)
    else:
        return np.nan


def search_query():
    """
    Executes the search query.

    Returns:
    DataFrame: The search result DataFrame.
    """
    global indexes
    df = read_data()
    single = df.loc[0, :].copy()
    indexes = index_data(df, indexes)
    save_index_to_json(indexes, 'indexes.json')
    indexes = load_index_from_json('indexes.json')
    data = {'Title': df['Title'].to_list(),
            'Authors': df['Authors'].to_list(),
            'Publication Year': df['Publication Year'].to_list(),
            'Publication Link': df['Publication Link'].to_list(),
            'Authors Profile': df['Authors Profile'].to_list()
            }
    df = pd.DataFrame(data)
    df = df.style.format({'Publication Link': fun, 'Authors Profile': fun})
    return df
