import config
import constants
import helper_functions
import mappers
import logging

logging.info("tenant_config_migration_workflows | START")


def get_headers(api_token):
    return {"Content-Type": "application/json", "api-token": api_token}


def map_permission_exceptions(
    permissionExceptions, start_domain, post_domain, start_head, post_head
):
    all_source_roles = helper_functions.get_request(
        start_domain, constants.ENDPOINT_ROLES, start_head
    )
    mapped_source_roles = mappers.map_roles(all_source_roles)
    all_source_project_permissions = helper_functions.get_request(
        start_domain,
        f"{constants.ENDPOINT_ROLES}/project-permissions",
        start_head,
    )

    all_dest_project_permissions = helper_functions.get_request(
        post_domain,
        f"{constants.ENDPOINT_ROLES}/project-permissions",
        post_head,
    )
    all_dest_custom_fields = helper_functions.get_request(
        post_domain, constants.ENDPOINT_CUSTOM_FIELDS, post_head
    )

    all_dest_roles = helper_functions.get_request(
        post_domain, constants.ENDPOINT_ROLES, post_head
    )
    mapped_dest_roles = mappers.map_roles(all_dest_roles)

    role_matches = helper_functions.find_matches(
        mapped_source_roles, mapped_dest_roles, "name"
    )

    permissionExceptions_to_return = []

    for permissionException in permissionExceptions:
        role = helper_functions.get_request(
            start_domain,
            f"{constants.ENDPOINT_ROLES}/{permissionException['role']['id']}",
            start_head,
        )

        if role["name"] in role_matches:
            permissionException["roleId"] = role_matches[role["name"]]
        else:
            logging.error(f"Role {role['name']} not found in destination domain")
            return

        project_permissions_to_return = []
        for projectPermission in permissionException["projectPermissions"]:
            project_permission_name = next(
                (
                    perm["name"]
                    for perm in all_source_project_permissions["_embedded"]["items"]
                    if perm["id"] == projectPermission
                ),
                None,
            )
            if project_permission_name:
                dest_project_permission_id = next(
                    (
                        perm["id"]
                        for perm in all_dest_project_permissions["_embedded"]["items"]
                        if perm["name"] == project_permission_name
                    ),
                    None,
                )
                if dest_project_permission_id:
                    project_permissions_to_return.append(dest_project_permission_id)
                else:
                    logging.error(
                        f"Project permission {project_permission_name} not found in destination domain"
                    )
                    return
            else:
                logging.error(
                    f"Project permission ID {projectPermission['id']} not found in source domain"
                )
                return

        custom_field_premissions_to_return = []
        ids_already_mapped = []
        for customFieldPermission in permissionException["customFieldPermissions"]:
            custom_field_permission_name = customFieldPermission["customField"]["name"]
            if custom_field_permission_name:
                dest_custom_field_permission_id = next(
                    (
                        perm["id"]
                        for perm in all_dest_custom_fields["_embedded"]["items"]
                        if perm["name"] == custom_field_permission_name
                        and perm["id"] not in ids_already_mapped
                    ),
                    None,
                )

                print(
                    f"Processing custom field permission: {custom_field_permission_name} | ID: {dest_custom_field_permission_id}"
                )

                if dest_custom_field_permission_id:
                    custom_field_premissions_to_return.append(
                        {
                            "customFieldId": dest_custom_field_permission_id,
                            "accessLevel": customFieldPermission["accessLevel"],
                        }
                    )
                    ids_already_mapped.append(dest_custom_field_permission_id)
                else:
                    logging.error(
                        f"Custom field permission {custom_field_permission_name} not found in destination domain"
                    )

            else:
                logging.error(
                    f"Custom field permission ID {customFieldPermission['id']} not found in source domain"
                )

        permissionExceptions_to_return.append(
            {
                "roleId": permissionException["roleId"],
                "projectPermissions": project_permissions_to_return,
                "customFieldPermissions": custom_field_premissions_to_return,
            }
        )

    return permissionExceptions_to_return


def main(start_domain, post_domain, start_head, post_head):

    source_results_workflows = helper_functions.get_request(
        start_domain, constants.ENDPOINT_WORKFLOW, start_head
    )

    dest_results_workflows = helper_functions.get_request(
        post_domain, constants.ENDPOINT_WORKFLOW, post_head
    )

    source_mapped_workflows = mappers.map_workflows(source_results_workflows)
    dest_mapped_workflows = mappers.map_workflows(dest_results_workflows)

    matches_workflows = helper_functions.find_matches(
        source_mapped_workflows, dest_mapped_workflows, "referenceId"
    )

    workflows_to_migrate = []
    for workflow in source_mapped_workflows:
        if workflow["referenceId"] in matches_workflows:
            if (
                helper_functions.is_ir_object_same(workflow, dest_mapped_workflows)
                is False
            ):
                uuid = matches_workflows[workflow["referenceId"]]
                workflow_to_put = {
                    "id": uuid,
                    "name": workflow["name"],
                    "referenceId": workflow["referenceId"],
                    "description": workflow["description"],
                    "lockThreatModel": str(workflow["lockThreatModel"]),
                    "reports": {
                        "residualRisk": {
                            "watermark": workflow["reports"]["residualRisk"][
                                "watermark"
                            ],
                            "visible": str(
                                workflow["reports"]["residualRisk"]["visible"]
                            ),
                        },
                        "technicalThreatReport": {
                            "watermark": workflow["reports"]["technicalThreatReport"][
                                "watermark"
                            ],
                            "visible": str(
                                workflow["reports"]["technicalThreatReport"]["visible"]
                            ),
                        },
                        "technicalCountermeasureReport": {
                            "watermark": workflow["reports"][
                                "technicalCountermeasureReport"
                            ]["watermark"],
                            "visible": str(
                                workflow["reports"]["technicalCountermeasureReport"][
                                    "visible"
                                ]
                            ),
                        },
                        "complianceReport": {
                            "watermark": workflow["reports"]["complianceReport"][
                                "watermark"
                            ],
                            "visible": str(
                                workflow["reports"]["complianceReport"]["visible"]
                            ),
                        },
                    },
                    "permissionExceptions": map_permission_exceptions(
                        workflow["permissionExceptions"],
                        start_domain,
                        post_domain,
                        start_head,
                        post_head,
                    ),
                }
            else:
                logging.info(
                    f"Workflow with referenceId {workflow['referenceId']} already exists in destination"
                )
                continue
        else:
            workflow_to_put = {
                "name": workflow["name"],
                "referenceId": workflow["referenceId"],
                "description": workflow["description"],
                "lockThreatModel": str(workflow["lockThreatModel"]),
                "reports": {
                    "residualRisk": {
                        "watermark": workflow["reports"]["residualRisk"]["watermark"],
                        "visible": str(workflow["reports"]["residualRisk"]["visible"]),
                    },
                    "technicalThreatReport": {
                        "watermark": workflow["reports"]["technicalThreatReport"][
                            "watermark"
                        ],
                        "visible": str(
                            workflow["reports"]["technicalThreatReport"]["visible"]
                        ),
                    },
                    "technicalCountermeasureReport": {
                        "watermark": workflow["reports"][
                            "technicalCountermeasureReport"
                        ]["watermark"],
                        "visible": str(
                            workflow["reports"]["technicalCountermeasureReport"][
                                "visible"
                            ]
                        ),
                    },
                    "complianceReport": {
                        "watermark": workflow["reports"]["complianceReport"][
                            "watermark"
                        ],
                        "visible": str(
                            workflow["reports"]["complianceReport"]["visible"]
                        ),
                    },
                },
                "permissionExceptions": map_permission_exceptions(
                    workflow["permissionExceptions"],
                    start_domain,
                    post_domain,
                    start_head,
                    post_head,
                ),
            }

        workflows_to_migrate.append(workflow_to_put)

    if len(workflows_to_migrate) > 0:
        post_head = post_head
        post_head["X-Irius-Async"] = "True"

        build_response = {
            "workflow": workflows_to_migrate,
            "deleteReplacements": [],
        }

        helper_functions.put_request(
            "",
            build_response,
            post_domain + constants.ENDPOINT_WORKFLOW,
            post_head,
        )

    else:
        logging.info("No workflows to migrate")

    logging.info("tenant_config_migration_workflows | END")


if __name__ == "__main__":
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)
