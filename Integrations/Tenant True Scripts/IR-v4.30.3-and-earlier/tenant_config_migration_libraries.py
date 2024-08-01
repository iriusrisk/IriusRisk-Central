import pip._vendor.requests as requests
import sys
import os
import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_libraries(url, headers):
    #Fetch and log library data from API.
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info("Libraries fetched successfully.")
        return response.json()
    logging.error(f"Fetch failed. Status code: {response.status_code}")
    return None

def process_libraries_data(libraries_data):
    #Extract and return custom libraries from API response.
    return [
        {'id': item['id'], 'name': item['name'], 'referenceId': item.get('referenceId'), 'filePath': None}
        for item in libraries_data.get('_embedded', {}).get('items', [])
        if item.get('type', '').lower() == 'custom'
    ]

def export_libraries_to_xml(libraries_info, domain, headers):
    #Export libraries to XML, save files locally.
    if not os.path.exists('exports'):
        os.makedirs('exports')
    for library in libraries_info:
        export_url = f'{domain}/api/v2/libraries/{library["id"]}/export'
        response = requests.get(export_url, headers=headers)
        if response.status_code == 200:
            file_path = os.path.join('exports', f"{library['id']}.xml")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            library['filePath'] = file_path
            logging.info(f"Exported {library['id']}.")
        else:
            logging.error(f"Export failed for {library['id']}. Status: {response.status_code}")

def import_libraries(libraries_info, url, headers):
    #Import libraries from local XML files to the target system.
    for library in libraries_info:
        if library.get('filePath') and os.path.exists(library['filePath']):
            with open(library['filePath'], 'rb') as file:
                files = {'file': (os.path.basename(library['filePath']), file)}
                data = {"referenceId": library['referenceId'], "name": library['name']}
                response = requests.post(url, headers=headers, data=data, files=files)
                if response.status_code == 200:
                    logging.info(f"Imported {library['name']}.")
                else:
                    logging.error(f"Import failed for {library['name']}. Status: {response.status_code}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    start_url = f"{config.start_domain}/api/v2/libraries?size=10000"
    libraries_data = fetch_libraries(start_url, config.start_head)
    if libraries_data:
        libraries_info = process_libraries_data(libraries_data)
        export_libraries_to_xml(libraries_info, config.start_domain, config.start_head)
        import_libraries(libraries_info, f"{config.post_domain}/api/v2/libraries/import", config.post_head)
