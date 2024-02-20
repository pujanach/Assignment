import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import webbrowser
sample_db = pd.read_csv("data.csv")


def ui_main():
    class InvertedIndex:
        def __init__(self):
            self.index = {}

        def index_document(self, doc_id, text, field):
            # Tokenize text into terms
            terms = text.split()
            # Update index with terms and corresponding document IDs
            for term in terms:
                if term not in self.index:
                    self.index[term] = {}
                if doc_id not in self.index[term]:
                    self.index[term][doc_id] = set()
                self.index[term][doc_id].add(field)

        def search(self, query, field):
            terms = query.split()
            results = set(self.index.get(terms[0], {}).keys())
            for term in terms[1:]:
                results = results.intersection(self.index.get(term, {}).keys())

            # Filter results by selected field (either Title or Authors)
            filtered_results = []
            print(filtered_results)
            for doc_id in results:
                if field.lower() == 'title':
                    if query.lower() in df.loc[doc_id]['Title'].lower():
                        filtered_results.append(doc_id)
                elif field.lower() == 'authors':
                    if query.lower() in df.loc[doc_id]['Authors'].lower():
                        filtered_results.append(doc_id)
                elif field.lower() == 'publication year':
                    if query.lower() == str(df.loc[doc_id]['Publication Year']).lower():
                        filtered_results.append(doc_id)
            return filtered_results

    data = {
        'Title': sample_db['Title'].to_list(),
        'Authors': sample_db['Authors'].to_list(),
        'Publication Year': sample_db['Publication Year'].to_list(),
        'Publication Link': sample_db['Publication Link'].to_list(),
        'Authors Profile': sample_db['Authors Profile'].to_list()
    }
    df = pd.DataFrame(data)

    # Initialize an inverted index
    index = InvertedIndex()

    # Indexing publications dynamically based on field
    def index_based_on_field(field):
        index.index = {}
        for doc_id, row in df.iterrows():
            publication_data = row[field]
            index.index_document(doc_id, publication_data, field)

    # Example usage
    field_to_index = "Title"  # Change this to "Authors" to index based on authors
    index_based_on_field(field_to_index)

    # Create a Tkinter application
    root = tk.Tk()
    root.title("Inverted Index Search")

    # Load and resize the logo
    logo_image = Image.open("coventry_university_logo.png")
    logo_image = logo_image.resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Create a frame to hold the search input and results
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Display the logo in the top left corner
    logo_label = ttk.Label(frame, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference
    logo_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    # Search Engine Title Label
    search_engine_label = ttk.Label(
        frame, text="Search engine", font=("Arial Bold", 18))
    search_engine_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    # Create a label for the search query
    ttk.Label(frame, text="Search Query:").grid(
        row=1, column=0, padx=5, pady=5, sticky=tk.W)
    query_entry = ttk.Entry(frame, width=50)
    query_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

    # Create a dropdown menu for selecting the search field
    selected_field = tk.StringVar()
    selected_field.set("None")  # Set the default value to "None"

    def update_selected_field(value):
        nonlocal field_to_index
        field_to_index = value
        if field_to_index != "None":
            # Re-index based on the selected field
            index_based_on_field(field_to_index)
        else:
            # Set a default field if "None" is selected
            index_based_on_field("Title")
    field_options = ["None", "Title", "Authors"]  # Include "None" as an option
    field_dropdown = ttk.OptionMenu(
        frame, selected_field, *field_options, command=update_selected_field)
    field_dropdown.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)

    # Create a treeview to display search results in table format
    result_columns = list(df.columns)
    result_tree = ttk.Treeview(frame, columns=result_columns, show="headings")
    for col in result_columns:
        result_tree.heading(col, text=col)
    result_tree.grid(row=2, column=0, columnspan=3,
                     padx=5, pady=5, sticky=(tk.W, tk.E))

    # Function to handle search button click event
    def search():
        query = query_entry.get()
        field = selected_field.get()
        # Call the search method of the index object
        results = index.search(query, field)
        result_tree.delete(*result_tree.get_children())
        for doc_id in results:
            row_data = df.loc[[doc_id]].values.tolist()[0]
            result_tree.insert("", "end", values=row_data)

    def open_link(event):
        col = result_tree.identify_column(event.x)
        # Check if the click occurred in the fourth column (Website column)
        if col == '#4':
            item = result_tree.identify_row(event.y)
            url = result_tree.item(item, 'values')[3]
            webbrowser.open_new(url)
        # Check if the click occurred in the fourth column (Website column)
        if col == '#5':
            item = result_tree.identify_row(event.y)
            url = result_tree.item(item, 'values')[4]
            webbrowser.open_new(url)

    # Create a search button
    search_button = ttk.Button(frame, text="Search", command=search)
    search_button.grid(row=1, column=3, padx=5, pady=5, sticky=tk.E)

    # Bind event to make links clickable
    result_tree.bind('<Button-1>', open_link)

    root.mainloop()
