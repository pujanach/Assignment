import requests
from bs4 import BeautifulSoup


def get_url(url):
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            # Find the anchor tag with class "portal_link" and text "Research output"
            research_output_link_element = soup.find(
                "a", class_="portal_link", text="Research output"
            )

            if research_output_link_element:
                # Get the URL linked to the element
                research_output_link = research_output_link_element["href"]

                # Construct the full URL if it's relative
                if research_output_link.startswith("/"):
                    research_output_link = (
                        "https://pureportal.coventry.ac.uk" + research_output_link
                    )

                # Return the research output URL
                return research_output_link
            else:
                print("Error: Research output element not found on the page.")
                return None
        else:
            # If the request was not successful, print an error message
            print(
                "Error: Unable to fetch data from the specified URL. Status code:",
                response.status_code,
            )
            return None
    except Exception as e:
        # Handle any exceptions that occur during the process
        print("An error occurred:", str(e))
        return None
