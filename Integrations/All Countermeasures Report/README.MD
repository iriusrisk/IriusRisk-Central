# Purpose 

The purpose of this script is to call all countermeasures from all libraries stored within your iriusrisk instance. 

# Requirements

1. Set up the virtual environment

```bash
python3 -m menv all-CM-Report
```

Activate the virtual environment
```bash
source all-CM-Report/bin/activate
```

2. Clone the repo into this environment

```bash
git clone https://github.com/IriusRisk/IriusRisk-Central.git
```
Navigate to the 'All Countermeasures Report'

```bash
cd Integrations/'All Countermeasures Report'/
```

3. Edit the config file with the following values defined in the same directory: 

```python
  api_key = '{your_api_key}'
  sub_domain = '{your_full_domain_minus_the_api_endpoint_data}' # for example https://demo.iriusrisk.com
```

2. Install the required packages

```bash
pip install -r requirements.txt
```

```bash
pip install pandas requests tqdm bs4 openpyxl
```

# Execution

Open the terminal, call the script

Example: 

```bash
   python3 get_library_details_v1.py
```

# Output
The output of this will print to the same directory and will include a json file and an xlsx file. 
