import pip._vendor.requests as requests
import sys
import json
import config

def get_api_data(url, headers):
    """Function to perform a GET request."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("GET request successful")
        return response.json()
    elif response.status_code == 401:
        print("User is unauthorized. Please check your API token and permissions.")
        sys.exit()
    else:
        print(f"GET request failed for {url}")
        return None

def post_api_data(url, headers, data):
    """Function to perform a POST request."""
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("POST successful")
        return response.json()
    elif response.status_code == 401:
        print("User is unauthorized. Please check your API token and permissions.")
        sys.exit()
    else:
        print(f"POST request failed for {url}")
        return None

def filter_data(items):
    """Function to filter the required data fields."""
    return [{f"referenceId": item['referenceId'],
             "name": item['name'],
             "description": item['description'],
             "trustRating": item['trustRating']} for item in items]

def main():
    # Initialize environment
    start_url = config.start_domain + '/api/v2/trust-zones'
    print(start_url)
    post_url = config.post_domain + '/api/v2/trust-zones'
    print(post_url)
    # Get data from the API
    data = get_api_data(start_url, config.start_head)
    if data:
        items = data['_embedded']['items']
        filtered_data = filter_data(items)
    
        # Post data to the API
        for item in filtered_data:
            post_response = post_api_data(post_url, {'api-token': config.post_apitoken}, item)
            if not post_response:
                print(f"Failed to post data for {item['name']}.")

if __name__ == "__main__":
    main()
