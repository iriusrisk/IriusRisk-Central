# IriusRisk V1/V2 Migration Tool - Web Interface (GUI)

A user-friendly web interface for transferring risk patterns from v2 components to their v1 (deprecated) counterparts in IriusRisk. This project aims to assist customers with updating any threat models with deprecated content through an intuitive graphical interface.

This was tested against v4.46 of IriusRisk.

## 📋 Project Overview

This tool provides a modern web interface built with Streamlit that automates the process of collecting, mapping, and transferring risk patterns between component versions, ensuring that deprecated v1 components receive the latest security content from their modern v2 equivalents.

**Why does this exist?**

IriusRisk allows you to switch out components and this feature will allow you to replace a deprecated v1 component for a new v2 component **BUT** it will remove any content for that component fully from project. To facilitate this transfer, this project will help you import the new v2 content onto the existing v1 components across the full tenant. This means that all of your v1 components will now have v2 content side by side your existing v1 content.

## 🎯 Features

- ✅ **Web-Based Interface**: Modern, intuitive Streamlit web application
- ✅ **Real-time Progress**: Live migration output streaming
- ✅ **Easy Configuration**: Point-and-click credential setup
- ✅ **Visual Feedback**: Progress indicators and status updates
- ✅ **Log Management**: View, download, and clear logs from the interface
- ✅ **IriusRisk Branding**: Professional styling with IriusRisk colors
- ✅ **Prerequisites Validation**: Automatic checks before migration starts
- ✅ **Results Summary**: Visual overview of migration outcomes

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

2. **Quick Launch** (recommended):
   ```bash
   ./run_streamlit.sh
   ```
   
   This script will:
   - Create virtual environment if needed
   - Install all dependencies
   - Launch the web interface

3. **Manual Setup** (alternative):
   ```bash
   # Set up virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Run Streamlit app
   streamlit run app.py
   ```

## 🌐 Web Interface Usage

### 1. **Access the Interface**
- Open your browser to `http://localhost:8501`
- The interface will load with IriusRisk branding

### 2. **Configure Credentials**
- Enter your **API Token** (automatically saved to .env)
- Enter your **Subdomain** (e.g., "r2", "demo")
- Credentials are validated and saved automatically

### 3. **Start Migration**
- Click **"🚀 Start Migration"** in the hero section, OR
- Use the **"🚀 Run Full Migration"** button in the configuration section
- **Advanced Options**: Enable "Test Mode" for faster validation

### 4. **Monitor Progress**
- **Real-time Output**: Live streaming of migration progress
- **Status Updates**: Clear indicators of current phase
- **Stop Option**: Ability to stop migration if needed

### 5. **Review Results**
- **Migration Summary**: Overview of generated files and statistics
- **Log Files**: Complete audit trail with timestamps
- **Download Logs**: Export logs for archival or analysis

## 🎨 Interface Features

### **Hero Section**
- **Smart Start Button**: Only enabled when ready to run
- **Status Awareness**: Shows current migration state
- **Quick Access**: One-click migration start

### **Configuration Panel**
- **Automatic .env Creation**: Credentials saved to environment file
- **Validation Feedback**: Real-time prerequisite checking
- **Test Mode Toggle**: Enable for faster execution with limited data

### **Migration Controls**
- **🚀 Run Full Migration**: Start complete migration process
- **🛑 Stop Migration**: Terminate running migration
- **📊 View Results Summary**: Display migration outcomes
- **🔄 Refresh Status**: Update interface state

### **Live Progress Monitoring**
```
🔄 Migration is currently running...

🌅 RADIANT SWING - Component Migration System
============================================================
Started at: 2025-10-11 14:30:15

📋 Phase 1: Collect V1 Components
============================================================
🚀 Starting Phase 1 at 14:30:16
🌐 Making API request to: https://r2.iriusrisk.com/...
✅ Found 45 v1 (deprecated) components
✅ Phase 1 completed successfully in 12.34 seconds
```

### **Log Management**
- **📄 View Logs**: Real-time log file display
- **🔄 Refresh Log**: Update log display with latest entries
- **💾 Download Log**: Export timestamped log files
- **🗑️ Clear Log**: Reset log file (maintains audit trail)

## 🎯 Migration Process

The web interface guides you through this automated sequence:

1. **Prerequisites Validation**
   - ✅ Check for required files
   - ✅ Validate API credentials
   - ✅ Verify phase scripts exist

2. **Phase 1**: Collect V1 Components
   - Real-time API progress updates
   - Component count display
   - Success/failure indicators

3. **Phase 2**: Collect V2 Components
   - Filtering progress visualization
   - Component statistics
   - Validation results

4. **Phase 4a**: Collect Risk Patterns
   - Risk pattern discovery progress
   - Mapping validation
   - Pattern count updates

5. **Phase 4b**: Transfer Risk Patterns
   - Transfer operation progress
   - Success/failure tracking
   - Final statistics

## 🎨 Customization

### **Adding IriusRisk Logo**

1. **Save logo file** in the `static/` directory:
   ```bash
   static/logo.svg        # Preferred: SVG format
   static/logo.png        # Alternative: PNG format
   ```

2. **Automatic Detection**: The interface will automatically detect and display your logo

### **Branding Colors**

The interface uses IriusRisk brand colors:
- **Primary Green**: `#00A86B` (buttons, success states)
- **Brand Blue**: `#2F6FED` (gradients, links)
- **Background**: `#FFFFFF` (clean, professional)
- **Secondary**: `#F8F9FA` (panels, containers)

### **Custom Styling**

Edit `styles/iriusrisk.css` to customize:
- Button colors and styles
- Card layouts and shadows
- Typography and spacing
- Hero section gradients

## 📊 Results & Analytics

### **Migration Summary Display**
```
📊 Migration Results Summary
✅ V1 (deprecated) components: 45 items
✅ V2 (modern) components: 156 items
✅ Risk patterns collected: 89 items
✅ Transfer results: Generated
✅ Migration process log: Generated
✅ Action log: Generated
```

### **Generated Files**
The interface tracks and displays all generated files:
- `v1_components.json` - Deprecated components
- `v2_components.json` - Modern components  
- `matching_risk_patterns.json` - Risk patterns for transfer
- `phase4b_transfer_results.json` - Transfer results
- `migration.log` - Complete process log
- `action.log` - Detailed operation log

## 📱 User Experience

### **Responsive Design**
- Works on desktop and tablet devices
- Clean, professional interface
- Intuitive navigation and controls

### **Real-time Feedback**
- Live progress updates during migration
- Clear success/error indicators
- Contextual help and guidance

### **Error Handling**
- Graceful error display and recovery
- Detailed error messages in logs
- Ability to retry after fixing issues

### **Accessibility**
- Focus-visible outlines for keyboard navigation
- High contrast colors for readability
- Clear typography and spacing

## 🔧 Configuration Files

### **Streamlit Configuration**
`.streamlit/config.toml`:
```toml
[theme]
base = "light"
primaryColor = "#00A86B"                 # Irius Green
backgroundColor = "#FFFFFF"              # Page background
secondaryBackgroundColor = "#F8F9FA"     # Panels/boxes
textColor = "#101418"                    # Body text
font = "sans serif"                      # Typography
```

### **Environment Variables**
`.env` (auto-created by interface):
```bash
API_TOKEN=your_iriusrisk_api_token
SUBDOMAIN=your_subdomain
```

## 🚀 Advanced Features

### **Test Mode**
- Enable via checkbox in Advanced Options
- Processes limited data for faster execution
- Perfect for validating setup and configuration
- Provides quick feedback for troubleshooting

### **Log File Management**
- **Real-time Viewing**: See logs update live during migration
- **Download Feature**: Export logs with timestamps for archival
- **Clear Functionality**: Reset logs while maintaining audit trail
- **Search and Filter**: Navigate through large log files

### **Session State Management**
- Maintains migration state across page refreshes
- Remembers configuration settings
- Preserves migration progress and results

## 🛠️ Troubleshooting

### **Common Interface Issues**

**Page Won't Load**
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Restart if needed  
./run_streamlit.sh
```

**Migration Button Disabled**
- ✅ Check API credentials are entered
- ✅ Verify prerequisites are met
- ✅ Ensure no migration is currently running

**Real-time Updates Not Working**
- ✅ Ensure browser allows real-time updates
- ✅ Check network connectivity
- ✅ Try refreshing the browser

### **Log Analysis**
- Use the "View Migration Log File" section
- Download logs for external analysis
- Check both live output and log files for complete picture

## 🌟 Benefits of Web Interface

### **For Business Users**
- ✅ **No Command Line**: Point-and-click simplicity
- ✅ **Visual Progress**: See exactly what's happening
- ✅ **Professional UI**: IriusRisk-branded interface
- ✅ **Easy Configuration**: No manual file editing

### **For IT Teams**
- ✅ **Real-time Monitoring**: Live migration progress
- ✅ **Complete Logging**: Full audit trail
- ✅ **Error Visibility**: Clear error reporting
- ✅ **Remote Access**: Run on server, access via browser

### **For Automation**
- ✅ **API Backend**: Same robust migration engine
- ✅ **Log Export**: Download results for processing
- ✅ **Session Management**: Handle long-running migrations
- ✅ **Status Monitoring**: Check progress remotely

## Support

For questions, issues, or contributions:
- 📧 Create an issue in this repository
- 📖 Check the interface logs for detailed error information
- 🔍 Use Test Mode to validate setup quickly
- 💬 Access help documentation within the interface

---

**Built for user-friendly migration management** 🎯