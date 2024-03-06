import requests
import config
import json

def get_libraries():
    url = f"{config.baseURL}/api/v1/libraries?max=100&index=0"
    headers = {
        'Accept': 'application/json',
        'api-token': config.api_token
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        class Library:
            def __init__(self, ref, name):
                self.ref = ref
                self.name = name

        libraries = []

        for item in data:
            library = Library(item['ref'], item['name'])
            libraries.append(library)

        all_library_refs = []

        for library in libraries:
            #print('ref:', library.ref)
            all_library_refs.append(library.ref)

        return(all_library_refs)

    else:
        print(f"Failed to fetch libraries. Status code: {response.status_code}")

get_libraries()
