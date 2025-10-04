# v1 to v2 component migrating tool

A comprehensive component migration tool for transferring risk patterns from v2 components to their v1 (deprecated) counterparts in IriusRisk. This project aims to assist customers with updating any threat models with deprecated content. 

This was tested against v4.46 of IriusRisk. 

## 📋 Project Overview

This tool automates the process of collecting, mapping, and transferring risk patterns between component versions, ensuring that deprecated v1 components receive the latest security content from their modern v2 equivalents.

**Why does this exist?**

IriusRisk allows you to switch out components and this feature will allow you to replace a deprecated v1 component for a new v2 component **BUT** it will remove any content for that component fully from project. To facilitate this transfer, this project will help you import the new v2 content onto the existing v1 components across the full tenant. This means that all of your v1 components will now have v2 content side by side your existing v1 content. 

## 🎯 Features

- ✅ **Component Collection**: Automatically collect v1 and v2 components via API 
- ✅ **Risk Pattern Transfer**: Bulk transfer risk patterns from v2 to v1 components
- ✅ **Cleanup & Testing**: Complete cleanup functionality for repeated testing
- ✅ **Comprehensive Logging**: Full audit trail of all operations
- ✅ **Rate Limiting**: API-friendly with configurable delays
- ✅ **Error Handling**: Robust error handling and recovery

## 📁 Project Structure

```
v1_v2_migration_tool/
├── README.md                           # This file
├── .env                               # Environment variables (API tokens)
├── src/                               # Source code
│   ├── phase1_collect_v1_components.py    # Collect deprecated components
│   ├── phase2_collect_v2_components.py    # Collect modern components  
│   ├── phase3_convert_csv_to_json.py      # Convert CSV mappings to JSON (not really needed anything longer but provided in case the csv file is ever updated to build new mappings for v1 to v2 components)
│   ├── phase4a_collect_risk_patterns.py   # Collect risk patterns from v2
│   ├── phase4b_transfer_risk_patterns.py  # Transfer patterns to v1
│   └── phase4_cleanup.py                  # Reset file for testing in a dev or UAT enviornment where you might want to clean up that environment. 
├── docs/                              # Documentation
    |--v1_v2_components_mappings.csv      # original mapping spreadsheet. Only needed if we post more updates later. 
├── tests/                             # Test files
└── Generated & existing Files:                   # Created by running phases
    ├── v1_components.json                 # V1 component list
    ├── v2_components.json                 # V2 component list
    ├── v1_v2_component_mappings.json      # Component mappings
    ├── matching_risk_patterns.json        # Risk pattern mappings
    ├── phase4b_transfer_results.json      # Transfer results
    ├── phase4_cleanup_results.json        # Cleanup results
    ├── action.log                          # Transfer operation log
    └── cleanup.log                         # Cleanup operation log
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with virtual environment
2. **IriusRisk API access** with valid API token
3. **OpenAI API key** (for Phase 3 AI mapping)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iriusrisk/IriusRisk-Central.git
   cd IriusRisk-Central/Integrations/v1_v2_migration_tool
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install requests python-dotenv openai
   ```
   or

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Edit .env file
   API_TOKEN=your_iriusrisk_api_token
   ```

## 📊 Usage Guide

### Run all at Once 
This will run through all phases back to back (minus Phase 3 because that mapping file has been provided already)

```bash
python3 main.py
```
**OR** run each phase one at a time

### Phase 1: Collect V1 (Deprecated) Components

Collects all components marked as deprecated from the IriusRisk API.

```bash
python3 src/phase1_collect_v1_components.py
```

**Output:** `v1_components.json` - List of deprecated components with IDs and metadata

### Phase 2: Collect V2 (Modern) Components  

Collects all non-deprecated components from the IriusRisk API.

```bash
python3 src/phase2_collect_v2_components.py
```

**Output:** `v2_components.json` - List of modern components with IDs and metadata

### Phase 3: Build Component Mappings

Converts existing CSV mappings to JSON format for processing.

```bash
python3 src/phase3_convert_csv_to_json.py
```

**Input:** `v1_v2_component_mappings.csv` - Pre-existing component mappings  
**Output:** `v1_v2_component_mappings.json` - JSON formatted mappings

This has already been done for you. The original csv is in the docs/ folder. This was used to build the json in this directory.

### Phase 4a: Collect Risk Patterns

Discovers and collects risk patterns attached to v2 components.

```bash
python3 src/phase4a_collect_risk_patterns.py
```

**Output:** `matching_risk_patterns.json` - Risk patterns with component mappings

### Phase 4b: Transfer Risk Patterns

Transfers risk patterns from v2 components to their v1 counterparts.

```bash
python3 src/phase4b_transfer_risk_patterns.py
```

**Output:** 
- `phase4b_transfer_results.json` - Detailed transfer results
- `action.log` - Complete operation log

### Phase 4 Cleanup: Remove Transferred Patterns

Removes all transferred risk patterns (useful for testing).

```bash
python3 src/phase4_cleanup.py
```

**Output:**
- `phase4_cleanup_results.json` - Cleanup results
- `cleanup.log` - Cleanup operation log

## 🔄 Testing Workflow

For repeated testing on the same tenant:

```bash
# 1. Transfer risk patterns
python3 src/phase4b_transfer_risk_patterns.py

# 2. Run your tests/validation
# ... your testing here ...

# 3. Clean up (reset tenant state)
python3 src/phase4_cleanup.py

# 4. Repeat as needed
```

## 📈 Statistics & Monitoring

### API Rate Limiting
- **Transfer Operations**: 1 second delay between API calls
- **Component Processing**: 2 seconds delay between components
- **Cleanup Operations**: 0.5 seconds delay between deletions

## 📝 Logging & Audit Trail

All operations are comprehensively logged:

- **action.log**: Transfer operations with timestamps, success/failure status
- **cleanup.log**: Cleanup operations with detailed results
- **Console Output**: Real-time progress and status updates
- **JSON Results**: Structured results for programmatic analysis

## 🛡️ Error Handling

- **API Failures**: Automatic retry logic with exponential backoff
- **Missing Components**: Graceful handling of missing v1/v2 mappings
- **Network Issues**: Request timeout and connection error handling
- **Data Validation**: Input validation and sanitization

## 🔧 Configuration

### Environment Variables (.env)
```bash
API_TOKEN=your_iriusrisk_api_token          # Required: IriusRisk API access
```

### API Endpoints Used
```bash
# Component Collection
GET /api/v2/components?filter='name'~'Deprecated'&size=200000
GET /api/v2/components?size=200000

# Risk Pattern Operations  
GET /api/v2/components/{id}/risk-patterns?page=0&size=200000
POST /api/v2/components/{component_id}/risk-patterns
DELETE /api/v2/components/{component_id}/risk-patterns/{risk_pattern_id}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

**API Authentication Errors**
```bash
# Check your API token in .env file
grep API_TOKEN .env
```

**Missing Components**
```bash
# Verify component files exist
ls -la *.json
```

**Rate Limiting Issues**
```bash
# Increase delays in transfer scripts (modify time.sleep() values)
```

## Support

For questions, issues, or contributions:
- 📧 Create an issue in this repository

---

**Built with ❤️ for IriusRisk component migration**/
