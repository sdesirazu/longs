from bs4 import BeautifulSoup
import requests
import yfinance as yf
import pandas_ta as ta
import pandas as pd

def retrieve_fred():
    url = 'https://fred.stlouisfed.org/series/STLFSI4'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.text
    else:
        print("Failed to retrieve the data.")

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the specific element containing the STLFSI4 value
    # This will depend on the structure of the HTML. For example:
    # If the value is in a specific tag, you can use:
    # value_element = soup.find('tag_name', {'class': 'class_name'})

    # For demonstration, let's assume the value is in a <div> with a specific class
    # Adjust the selector based on the actual HTML structure
    value_element = soup.find('span', class_='series-meta-observation-value')  # Replace with actual class name

    if value_element:
        stlfsi4_value = value_element.text.strip()
        print(f'STLFSI4 Value: {stlfsi4_value}')
        return(stlfsi4_value)
    else:
        print("STLFSI4 value not found.")

