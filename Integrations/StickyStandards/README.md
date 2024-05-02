## Sticky Standards program

Using standards within IriusRisk is a good way to triage countermeasures based on specific needs. By applying 
a standard, you allow IriusRisk to calculate which countermeasures need to be implemented to achieve a particular
goal, for instance, to be GDPR-compliant. Unfortunately, applying a standard is a one-off--it makes changes
to the countermeasures at that point in time, but won't alter new countermeasures added after the fact.

StickyStandards allows you to apply a standard to a project which is then applied to any new countermeasures
added in the future. It is administered via a project's architectural diagram; as long as a standard is
selected, relevant countermeasures will automatically be marked "required."

Enabling sticky standards for a given environment requires running a Python-based script. It reads the standards
available to that instance (or a subset), creates UDTs (custom fields) at the project level to facilitate, and
imports a Rules library into the instance to create the architecture questionnaire and to apply and standards
marked as being "sticky."
