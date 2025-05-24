import requests
from datetime import date

# Define the URL
def retrieve_fear_and_greed():

    today = str(date.today())

    url = 'https://production.dataviz.cnn.io/index/fearandgreed/graphdata/'+today

    # Define the headers
    headers = {
        'authority': 'production.dataviz.cnn.io',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'if-none-match': 'W/-1392655433487906560',
        'origin': 'https://edition.cnn.com',
        'referer': 'https://edition.cnn.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Print the response data (JSON or text)
        content = response.json()  # Assuming the response is in JSON format
        return(content['fear_and_greed']['score'])
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    return 0


