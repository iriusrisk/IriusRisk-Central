import logging
import config
import constants
import helper_functions
import mappers
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_dest_roles_permissions(permission_type):
    dest_role_permissions = helper_functions.get_request(
        config.dest_domain,
        f"{constants.ENDPOINT_ROLES}/{permission_type}",
        config.dest_head,
    )

    return dest_role_permissions["_embedded"]["items"]


def get_custom_fields(domain, headers):
    custom_fields = helper_functions.get_request(
        domain, constants.ENDPOINT_CUSTOM_FIELDS, headers
    )
    return custom_fields


def main(source_domain, dest_domain, source_head, dest_head):
    try:
        logging.info("tenant_config_migration_permissions | START")

        # Get roles from both domains
        source_roles = helper_functions.get_request(
            config.source_domain, constants.ENDPOINT_ROLES, config.source_head
        )
        dest_roles = helper_functions.get_request(
            config.dest_domain, constants.ENDPOINT_ROLES, config.dest_head
        )

        # Map roles
        source_mapped = mappers.map_roles(source_roles)
        dest_mapped = mappers.map_roles(dest_roles)

        # Find matches
        matches = helper_functions.find_matches(source_mapped, dest_mapped, "name")

        # Get destination project permissions
        dest_roles_project_permissions = get_dest_roles_permissions(
            "project-permissions"
        )

        # Get destination global permissions
        dest_roles_global_permissions = get_dest_roles_permissions("global-permissions")

        # get custom fields
        custom_fields = get_custom_fields(dest_domain, dest_head)

        # Migrate roles
        for role in source_mapped:
            name = role.get("name")
            source_uuid = role.get("id")
            if name in matches:
                dest_uuid = matches[name]
                if (
                    helper_functions.is_ir_object_same_custom_field(
                        role, dest_mapped, "name"
                    )
                    is False
                ):
                    helper_functions.put_request(
                        dest_uuid,
                        role,
                    dest_domain + constants.ENDPOINT_ROLES,
                        dest_head,
                    )
                    role["id"] = dest_uuid
                    logging.info(f"Updated role with UUID: {dest_uuid}")
                else:
                    logging.info(f"Role with name {name} already exists in destination")
                    role["id"] = dest_uuid
            else:
                role_to_post = {
                    "name": role["name"],
                    "description": role["description"],
                }
                new_role = helper_functions.dest_request(
                    role_to_post,
                    dest_domain + constants.ENDPOINT_ROLES,
                    dest_head,
                )
                role["id"] = new_role["id"]
                logging.info(f"Created new role: {role}")

            # Migrate permissions
            migrate_custom_fields_permissions(
                source_mapped,
                source_uuid,
                role["id"],
                custom_fields,
                "custom-fields-permissions",
                source_domain,
                source_head,
                dest_domain,
                dest_head,
            )
            migrate_permissions(
                source_mapped,
                source_uuid,
                role["id"],
                dest_roles_project_permissions,
                "project-permissions",
                source_domain,
                source_head,
                dest_domain,
                dest_head,
            )
            migrate_permissions(
                source_mapped,
                source_uuid,
                role["id"],
                dest_roles_global_permissions,
                "global-permissions",
                source_domain,
                source_head,
                dest_domain,
                dest_head,
            )

        logging.info("tenant_config_migration_permissions | END")
    except Exception as e:
        logging.error(f"Error during roles migration: {e}")


def migrate_custom_fields_permissions(
    source_roles, source_uuid, dest_role_id, dest_role_permissions, permission_type, source_domain, source_head, dest_domain, dest_head
):
    try:
        for role in source_roles:
            permissions_to_put = []
            role_permissions = helper_functions.get_request(
                source_domain,
                f"{constants.ENDPOINT_ROLES}/{source_uuid}/custom-field-permissions",
                source_head,
            )

            for role_permission in role_permissions["_embedded"]["items"]:
                for dest_role_permission in dest_role_permissions["_embedded"]["items"]:
                    if (
                        role_permission["customField"]["name"]
                        == dest_role_permission["name"]
                    ):
                        permissions_to_put.append(
                            {
                                "customFieldId": dest_role_permission["id"],
                                "accessLevel": role_permission["accessLevel"],
                            }
                        )

            if len(permissions_to_put) > 0:
                # Post permissions
                dest_head["X-Irius-Async"] = "True"
                helper_functions.put_request(
                    "",
                    permissions_to_put,
                    f"{dest_domain}{constants.ENDPOINT_ROLES}/{dest_role_id}/custom-field-permissions/bulk",
                    dest_head,
                )
                logging.info(f"Put {permission_type} for role ID: {role['id']}")
                # Sleep for 30 seconds to allow permissions to be applied
                logging.info("Sleeping for 15 seconds to allow permissions to be applied...")
                time.sleep(15)
                logging.info("Resuming...")

    except Exception as e:
        logging.error(f"Error during {permission_type} migration: {e}")


def migrate_permissions(
    source_roles, source_uuid, dest_role_id, dest_role_permissions, permission_type, source_domain, source_head, dest_domain, dest_head
):
    try:
        for role in source_roles:
            permissions_to_post = []
            role_permissions = helper_functions.get_request(
                source_domain,
                f"{constants.ENDPOINT_ROLES}/{source_uuid}/{permission_type}",
                source_head,
            )
            for this_role_permission in role_permissions["_embedded"]["items"]:
                for dest_role_permission in dest_role_permissions:
                    if this_role_permission["name"] == dest_role_permission["name"]:
                        permissions_to_post.append(dest_role_permission["id"])

            if len(permissions_to_post) > 0:
                # Post permissions
                dest_head["X-Irius-Async"] = "True"
                json_to_post = {"permissions": permissions_to_post}
                helper_functions.dest_request(
                    json_to_post,
                    f"{dest_domain}{constants.ENDPOINT_ROLES}/{dest_role_id}/{permission_type}/bulk",
                    dest_head,
                )
                logging.info(f"Posted {permission_type} for role ID: {role['id']}")
    except Exception as e:
        logging.error(f"Error during {permission_type} migration: {e}")


if __name__ == "__main__":
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)
