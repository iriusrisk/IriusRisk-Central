import logging
import helper_functions
import constants
import config
import mappers

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(source_domain, dest_domain, source_head, dest_head):
    # Get data from the API
    source_response = helper_functions.get_request(
        source_domain, constants.ENDPOINT_TRUST_ZONES, source_head
    )
    destination_response = helper_functions.get_request(
        dest_domain, constants.ENDPOINT_TRUST_ZONES, dest_head
    )
    if source_response:
        source_mapped = mappers.map_trust_zones(source_response)
        destination_mapped = mappers.map_trust_zones(destination_response)

        matches = helper_functions.find_matches(
            source_mapped, destination_mapped, "referenceId"
        )

        for item in source_mapped:
            if item["referenceId"] in matches:
                if (
                    helper_functions.is_ir_object_same(item, destination_mapped)
                    is False
                ):
                    uuid = matches[item["referenceId"]]
                    helper_functions.put_request(
                        uuid,
                        item,
                        dest_domain + constants.ENDPOINT_TRUST_ZONES,
                        dest_head,
                    )
                    logging.info(f"PUT - Updated trust zone {uuid}")
                else:
                    logging.info(f"Trust zone [{item['name']}] is the same")
            else:
                del item["id"]
                helper_functions.post_request(
                    item,
                    dest_domain + constants.ENDPOINT_TRUST_ZONES,
                    dest_head,
                )
                logging.info(f"POST - Posted trust zone {item['name']}")

if __name__ == "__main__":
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)