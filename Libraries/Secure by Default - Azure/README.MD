# Purpose 

The purpose of this library is to showcase the value of having "secure by default" controls in place AND tuning your IriusRisk library to reflect this approach

# How it was created

The library content was exported from IriusRisk through the API and then frequency analysis was performed on grouped sets of similar controls. 

From that output, sets of rules were created that automatically mark those sets of countermeasures as implemented. 

Those secure by default statements are as follows: 

1. All admins have individual accounts
2. Audit logs are exported for storage by default
3. Azure cloud roles are configured and defined
4. Azure defender is enabled by default
5. Azure instances are in different vnets
6. Azure resource groups are managed from an approved location
7. Diagnostics logs are enabled
8. Managed identities are used
9. Network based IPS/IDS  are deployed by default
10. NSG Flow logs are enabled
11. NSGs are as restrictive as possible
12. NSGs block incoming traffic from 0.0.0.0/0 by default
13. Password expiration is set by default
14. PIM enabled for admins by default
15. RBAC applied to security groups by default
16. Security center security policy set by default
17. Service tags are used in place of ip addresses
18. Security center's adaptive hardening in place by default
19. User acess is recertified periodically by default
20. Mechanisms are in place to enforce and monitor for least privilege
21. MFA is enabled by default

# Alterations

If any of these statements are not true (in context of Azure), the rule can be removed or commented out in the Drool to disable it. 

# Import

Download the library xml and import into your tenant through the Risk Pattern Libraries

Risk Pattern Libraries > Import Library > Select a file > Import
