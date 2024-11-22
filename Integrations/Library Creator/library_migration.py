import config
import constants
import helper_functions
import logging

source_library_endpoint = config.source_domain + constants.ENDPOINT_LIBRARIES
dest_library_endpoint = config.dest_domain + constants.ENDPOINT_LIBRARIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def find_matching_libraries(all_source_libraries, all_dest_libraries):


    matches = helper_functions.find_matches(all_source_libraries["_embedded"]["items"], all_dest_libraries["_embedded"]["items"], "referenceId")

    return matches

def migrate_libraries():

    all_source_libraries = helper_functions.get_request(config.source_domain, constants.ENDPOINT_LIBRARIES, config.source_head)
    all_dest_libraries = helper_functions.get_request(config.dest_domain, constants.ENDPOINT_LIBRARIES, config.dest_head)

    matching_libraries = find_matching_libraries(all_source_libraries, all_dest_libraries)

    for library in all_source_libraries["_embedded"]["items"]:
        if library["referenceId"] in matching_libraries:
            logging.info(f"Library {library['name']} already exists in destination")
        else:
            handle_library(library, config.dest_head)


