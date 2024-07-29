# Testing warning

This content was produced before IriusRisk released its "v2" style AWS components. This will need to be tested in your instance prior to being moved into production. 

# Purpose 

The purpose of this library is to showcase the value of having "secure by default" controls in place AND tuning your IriusRisk library to reflect this approach

# How it was created

The library content was exported from IriusRisk through the API and then frequency analysis was performed on grouped sets of similar controls. 

From that output, sets of rules were created that automatically mark those sets of countermeasures as implemented. 

Those secure by default statements are as follows: 

1. Access to AWS resources are managed with IAM
2. S3 encryption by default
3. All resources are tagged by default
4. VPC security groups are used by default
5. Ingress from 0.0.0.0 are blocked on all ports
6. S3 public access is restricted by default
7. EC2 instanced launched into VPC by default
8. MFA enabled for IAM and Room users by default
9. Strong password policy by default
10. Privileges are allocated by groups by roles by default
11. SNS topics are used for sending out notifications by default
12. AWS configuration changes alerts are configured by default
13. IAM users have individual accounts
14. VPC endpoint policies are configured by default
15. VPC flow logs are enabled by default
16. Server side and in transit encryption are in place by default
17. Cloudtrail logs are logged to a dedicated and central S3 bucket by default



# Alterations

If any of these statements are not true (in context of AWS), the rule can be removed or commented out in the Drool to disable it. 

# Import

Download the library xml and import into your tenant through the Risk Pattern Libraries

Risk Pattern Libraries > Import Library > Select a file > Import
