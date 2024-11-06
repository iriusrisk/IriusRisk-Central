import helper_functions
import config
import constants
import logging
import mappers

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("tenant_config_migration_security_classifications | START")

def is_role_same(role, destination_roles):
    referenceId = role["referenceId"]
    for dest_role in destination_roles:
        if referenceId == dest_role["referenceId"]:
            del role["id"]
            del dest_role["id"]
            if role == dest_role:
                return True
            else:
                return False
    return False


domain_1_results = helper_functions.get_request(
    config.start_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, config.start_head
)
domain_2_results = helper_functions.get_request(
    config.post_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, config.post_head
)

domain_1_mapped = mappers.map_security_classifications(domain_1_results)
domain_2_mapped = mappers.map_security_classifications(domain_2_results)

matches = helper_functions.find_matches(domain_1_mapped, domain_2_mapped, "referenceId")

for role in domain_1_mapped:
    if role["referenceId"] in matches:
        if is_role_same(role, domain_2_mapped) is False:
            uuid = matches[role["referenceId"]]
            del role["referenceId"]
            helper_functions.put_request(
                uuid,
                role,
                config.post_domain + constants.ENDPOINT_SECURITY_CLASSIFICATIONS,
                config.post_head,
            )
    else:
        del role["id"]
        helper_functions.post_request(
            role,
            config.post_domain + constants.ENDPOINT_SECURITY_CLASSIFICATIONS,
            config.post_head,
        )

logging.info("tenant_config_migration_security_classifications | END")
