import config
import constants
import helper_functions
import mappers
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
def main(start_domain, post_domain, start_head, post_head):
    logging.info("tenant_config_migration_BUs | START")\

    source_results = helper_functions.get_request(
        start_domain, constants.ENDPOINT_BUSINESS_UNIT, start_head
    )

    dest_results = helper_functions.get_request(
        post_domain, constants.ENDPOINT_BUSINESS_UNIT, post_head
    )

    source_mapped = mappers.map_business_units(source_results)
    dest_mapped = mappers.map_business_units(dest_results)

    matches = helper_functions.find_matches(source_mapped, dest_mapped, "referenceId")

    for business_unit in source_mapped:
        if business_unit["referenceId"] in matches:
            if helper_functions.is_ir_object_same(business_unit, dest_mapped) is False:
                uuid = matches[business_unit["referenceId"]]
                del business_unit["referenceId"]
                helper_functions.put_request(
                    uuid,
                    business_unit,
                    post_domain + constants.ENDPOINT_BUSINESS_UNIT,
                    post_head,
                )
        else:
            del business_unit["id"]
            helper_functions.post_request(
                business_unit,
                post_domain + constants.ENDPOINT_BUSINESS_UNIT,
                post_head,
            )

    logging.info("tenant_config_migration_BUs | END")

if __name__ == "__main__":
    logging.info("tenant_config_migration_BUs | START")
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)
    logging.info("tenant_config_migration | END")
