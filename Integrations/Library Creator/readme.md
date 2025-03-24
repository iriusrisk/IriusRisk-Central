# 🛠️ IriusRisk Library Creation Script

This script automates the creation of security-related entities such as libraries, risk patterns, use cases, threats, weaknesses, and countermeasures in IriusRisk using its API. It reads from an Excel spreadsheet and interacts with the IriusRisk API to create or skip entities based on their existence. The script includes caching, retries, and detailed logging.

---

## ✅ Prerequisites

Before using this script, ensure you have the following:

1. **🔐 IriusRisk Account**  
   An IriusRisk account with permissions to create entities.

2. **🔑 API Key**  
   Generate an API token in IriusRisk and set the following environment variables:

   - **Option 1: Using a `.env` file (recommended for local use)**  
     Create a `.env` file in the root directory:
     ```env
     IRIUSRISK_API_URL=https://your.iriusrisk.instance/api/v1
     IRIUSRISK_API_TOKEN=your-api-token-here
     ```

   - **Option 2: Export in terminal**  
     ```bash
     export IRIUSRISK_API_URL=https://your-tenant.iriusrisk.com
     export IRIUSRISK_API_TOKEN=your-api-token-here
     ```

3. **🐍 Python Environment**  
   Python 3.7+ is required.

4. **📦 Required Libraries**  
   Create a `requirements.txt` file with the following:
   ```
   pandas
   openpyxl
   requests
   python-dotenv
   ```
   Then install them:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📝 Excel Format

The input Excel file must contain a sheet with the following columns:

| Column          | Description                                      |
|------------------|--------------------------------------------------|
| Library          | Name of the library                             |
| Risk_Pattern     | Name of the risk pattern                        |
| Use_Case         | Name of the use case                            |
| Threat           | Threat name                                     |
| Threat_Desc      | Threat description                              |
| Weakness         | Weakness name                                   |
| CM               | Countermeasure name                             |
| CM_Desc          | Countermeasure description                      |
| standardref      | Reference ID of the overarching standard        |
| standardname     | Name of the standard                            |
| supported standardref | Specific reference within the standard (e.g., CWE-79) |

⚠️ Reference IDs are auto-generated from names using safe formatting (e.g., spaces replaced with `-` or `_`).

---

## 🚀 Usage

1. **Run the script**  
   ```bash
   python library_creator.py
   ```

2. **Provide spreadsheet details**  
   You’ll be prompted to enter:
   - Location of your `.xlsx` spreadsheet
   - Name of the spreadsheet sheet

   Example:
   ```
   "C:\Users\you\Documents\library_data.xlsx"
   Sheet1
   ```

3. **Structure Preview Before Creation**

   The structure is displayed in a tree-like format:

   📦 Structure Preview

   Library: WebAppSecurity

   └── Risk Pattern: InputValidation

       └── Use Case: SQL Injection

           ├── Threat: SQLi Attack

           │   ├── Weakness: Unsanitized Input

           │   └── Countermeasure: Parameterized Queries

   This allows you to visually inspect how your spreadsheet entries map to the IriusRisk hierarchy — including relationships between libraries, risk patterns, use cases, threats, weaknesses, and countermeasures.

   #### ✅ Confirmation Step

   After previewing the structure, the script will prompt:

   Proceed with actual creation? (yes/no):

   - If you type `yes`, the script will begin creating the content in IriusRisk.
   - Any other response will cancel execution safely.

   This provides a built-in validation checkpoint so you don’t make accidental changes.

4. **Script Behavior**  
   - Caches already created entities to avoid duplicates
   - Checks existence with GET requests (where supported)
   - Treats 400 “already exists” errors as successful
   - Logs to `library_creator.log` and terminal

---

## 🧾 Logging & Output

- Output is printed in real-time to your terminal
- Each entity created or skipped is clearly reported
- Start and end of the script run are logged


---

## 🧪 Troubleshooting

- **Script not doing anything?**  
  - Ensure the `.env` file exists or environment variables are set
  - Verify Excel path and sheet name are valid
  - Check `library_creator.log` for errors

- **Getting 400s?**  
  - These are handled as “already exists” and logged for review.

- **Want to test first?**  
  - Use a spreadsheet with a few rows to verify behavior.

---

⚠️ **Disclaimer**  
Use this script responsibly. Ensure you have the necessary permissions and approvals before making changes to your IriusRisk instance. This tool is provided as-is and may require adjustments for your environment.

---

Happy threat modeling! 🔐✨
