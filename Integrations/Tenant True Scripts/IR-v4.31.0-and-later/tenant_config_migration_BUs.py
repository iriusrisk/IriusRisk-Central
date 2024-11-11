import config
import constants
import helper_functions
import mappers
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("tenant_config_migration_BUs | START")

source_domain = config.start_domain
source_headers = config.start_head

source_results = helper_functions.get_request(
    config.start_domain, constants.ENDPOINT_BUSINESS_UNIT, config.start_head
)

dest_results = helper_functions.get_request(
    config.post_domain, constants.ENDPOINT_BUSINESS_UNIT, config.post_head
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
                config.post_domain + constants.ENDPOINT_BUSINESS_UNIT,
                config.post_head,
            )
    else:
        del business_unit["id"]
        helper_functions.post_request(
            business_unit,
            config.post_domain + constants.ENDPOINT_BUSINESS_UNIT,
            config.post_head,
        )

logging.info("tenant_config_migration_BUs | END")
