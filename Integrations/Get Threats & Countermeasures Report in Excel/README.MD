# Purpose 

The purpose of this script is to pull a set of threats, their respective countermeasures and several additional values. 

# Requirements

1. Config file with the following values defined: 

```python
  api_key = '{your_api_key}'
  sub_domain = '{your_base_domain}'
```

2. Install the required packages

```python
    pip install requests
    pip install argparse
```

# Execution

1. Open the terminal, call the script, and provide the following arguments - python {script_name} {project_ref_ID} {workflow_status_filter_ref_ID}. 

Example: 

```commandline
   python .\get_threats_countermeasures_w_filter.py ado-demo new
```

# Output
The output of this will follow this format - 
```python
"Component {component_name} // Threat {count}: {threat_name} // Control: {control_name} // Control Risk - {control_risk_value} // {control_state} - {control_library}")
```
Currently this is filtering out any Implemented countermeasures and any countermeasure with a risk value of less than 50. Each threat is counted from the total list so when filtered, numbers will be missing. 

The final output will look like this - "Component Cardholder Data Environment (PCI-DSS) // Threat 108: An attacker gains access to cardholder data through security flaws in the application // Control: Train developers in up-to-date secure coding techniques // Control Risk - 80 // Required - PCI-DSS"

This printed output will also be printed to a spreadsheet in the same directory named output.xlsx

