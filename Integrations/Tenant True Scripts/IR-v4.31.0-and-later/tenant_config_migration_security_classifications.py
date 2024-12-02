import helper_functions
import config
import constants
import logging
import mappers

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(start_domain, post_domain, start_head, post_head):
    logging.info("tenant_config_migration_security_classifications | START")

    domain_1_results = helper_functions.get_request(
        start_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, start_head
    )
    domain_2_results = helper_functions.get_request(
        post_domain, constants.ENDPOINT_SECURITY_CLASSIFICATIONS, post_head
    )

    domain_1_mapped = mappers.map_security_classifications(domain_1_results)
    domain_2_mapped = mappers.map_security_classifications(domain_2_results)

    matches = helper_functions.find_matches(domain_1_mapped, domain_2_mapped, "referenceId")

    for role in domain_1_mapped:
        if role["referenceId"] in matches:
            if helper_functions.is_ir_object_same(role, domain_2_mapped) is False:
                uuid = matches[role["referenceId"]]
                del role["referenceId"]
                helper_functions.put_request(
                    uuid,
                    role,
                    post_domain + constants.ENDPOINT_SECURITY_CLASSIFICATIONS,
                    post_head,
                )
        else:
            del role["id"]
            helper_functions.post_request(
                role,
                post_domain + constants.ENDPOINT_SECURITY_CLASSIFICATIONS,
                post_head,
            )

    logging.info("tenant_config_migration_security_classifications | END")

if __name__ == "__main__":
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)