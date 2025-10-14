# IriusRisk V1/V2 Migration Tool - Command Line Interface

A comprehensive command-line tool for transferring risk patterns from v2 components to their v1 (deprecated) counterparts in IriusRisk. This project aims to assist customers with updating any threat models with deprecated content.

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
- ✅ **Command-Line Interface**: Perfect for automation and scripting

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with virtual environment
2. **IriusRisk API access** with valid API token

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
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Create .env file
   echo "API_TOKEN=your_iriusrisk_api_token" > .env
   echo "SUBDOMAIN=your_subdomain" >> .env
   ```

## 📊 Command-Line Usage

### Option 1: Run Complete Migration (Recommended)

Execute all phases in sequence:

```bash
python3 main.py
```

**With test mode** (limited data for faster execution):
```bash
python3 main.py --test
```

### Option 2: Run Individual Phases

Execute phases one at a time for more control:

#### Phase 1: Collect V1 (Deprecated) Components

Collects all components marked as deprecated from the IriusRisk API.

```bash
python3 src/phase1_collect_v1_components.py
```

**Output:** `v1_components.json` - List of deprecated components with IDs and metadata

#### Phase 2: Collect V2 (Modern) Components  

Collects all non-deprecated components from the IriusRisk API.

```bash
python3 src/phase2_collect_v2_components.py
```

**Output:** `v2_components.json` - List of modern components with IDs and metadata

#### Phase 4a: Collect Risk Patterns

Discovers and collects risk patterns attached to v2 components.

```bash
python3 src/phase4a_collect_risk_patterns.py
```

**Optional test mode:**
```bash
python3 src/phase4a_collect_risk_patterns.py --test
```

**Output:** `matching_risk_patterns.json` - Risk patterns with component mappings

#### Phase 4b: Transfer Risk Patterns

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
python3 main.py

# 2. Run your tests/validation
# ... your testing here ...

# 3. Clean up (reset tenant state)
python3 src/phase4_cleanup.py

# 4. Repeat as needed
```

## 📈 Execution Flow

The migration process follows this sequence:

1. **Prerequisites Check**: Validates all required files and configurations
2. **Phase 1**: Collect V1 (deprecated) components → `v1_components.json`
3. **Phase 2**: Collect V2 (modern) components → `v2_components.json`
4. **Phase 4a**: Collect risk patterns from V2 components → `matching_risk_patterns.json`
5. **Phase 4b**: Transfer risk patterns to V1 components → `phase4b_transfer_results.json`

## 📝 Output Files

After successful execution, you'll have these files:

```bash
v1_components.json                 # V1 component list
v2_components.json                 # V2 component list
v1_v2_component_mappings.json      # Component mappings (pre-existing)
matching_risk_patterns.json        # Risk patterns ready for transfer
phase4b_transfer_results.json      # Transfer results and statistics
action.log                         # Detailed transfer operations log
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
API_TOKEN=your_iriusrisk_api_token          # Required: IriusRisk API access
SUBDOMAIN=your_subdomain                    # Required: Your IriusRisk subdomain
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

## 📊 Statistics & Monitoring

### API Rate Limiting
- **Transfer Operations**: 1 second delay between API calls
- **Component Processing**: 2 seconds delay between components
- **Cleanup Operations**: 0.5 seconds delay between deletions

## 🛡️ Error Handling

- **API Failures**: Automatic retry logic with exponential backoff
- **Missing Components**: Graceful handling of missing v1/v2 mappings
- **Network Issues**: Request timeout and connection error handling
- **Data Validation**: Input validation and sanitization

## 📝 Logging & Audit Trail

All operations are comprehensively logged:

- **Console Output**: Real-time progress and status updates
- **action.log**: Transfer operations with timestamps, success/failure status
- **cleanup.log**: Cleanup operations with detailed results
- **JSON Results**: Structured results for programmatic analysis

## 🚀 Automation & Scripting

The CLI is perfect for automation scenarios:

```bash
#!/bin/bash
# Example automation script

echo "Starting IriusRisk V1/V2 Migration"

# Run migration
if python3 main.py --test; then
    echo "✅ Migration completed successfully"
    
    # Process results
    python3 -c "
import json
with open('phase4b_transfer_results.json', 'r') as f:
    results = json.load(f)
    print(f'Transferred {len(results)} risk patterns')
"
else
    echo "❌ Migration failed"
    exit 1
fi
```

## 🔧 Advanced Options

### Test Mode
Use `--test` flag with main.py or phase4a for faster execution:
- Processes limited data subset
- Useful for validating setup
- Faster feedback for testing

### Individual Phase Control
Run phases separately for:
- **Debugging**: Isolate issues to specific phases
- **Partial Updates**: Update only certain components
- **Performance**: Spread execution across time

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

### Log Analysis
```bash
# Check recent migration activity
tail -f action.log

# Count successful transfers
grep "SUCCESS" action.log | wc -l

# Check for errors
grep "ERROR\|FAIL" action.log
```

## 📦 Project Structure

```
v1_v2_migration_tool/
├── main.py                            # Main CLI orchestrator
├── .env                               # Environment variables
├── src/                               # Core migration scripts
│   ├── phase1_collect_v1_components.py
│   ├── phase2_collect_v2_components.py
│   ├── phase4a_collect_risk_patterns.py
│   ├── phase4b_transfer_risk_patterns.py
│   └── phase4_cleanup.py
├── v1_v2_component_mappings.json      # Component mappings
└── Generated Files:                   # Created by running phases
    ├── v1_components.json
    ├── v2_components.json
    ├── matching_risk_patterns.json
    ├── phase4b_transfer_results.json
    ├── action.log
    └── cleanup.log
```

## Support

For questions, issues, or contributions:
- 📧 Create an issue in this repository
- 📖 Check the logs for detailed error information
- 🔍 Use `--test` mode to validate setup

---

**Built for command-line automation and enterprise integration** ⚡