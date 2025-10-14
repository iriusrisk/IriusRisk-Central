# IriusRisk V1/V2 Component Migration Tool

A comprehensive tool for transferring risk patterns from v2 components to their v1 (deprecated) counterparts in IriusRisk. This project aims to assist customers with updating any threat models with deprecated content through both command-line and web interfaces.

This was tested against v4.46 of IriusRisk.

## 🚀 Choose Your Interface

This tool provides **two ways** to run the migration process:

### 📱 **Web Interface (Recommended for most users)**
- **User-friendly**: Point-and-click interface with real-time progress
- **Visual feedback**: Live migration streaming and progress indicators  
- **Easy setup**: Automatic credential management and validation
- **Professional UI**: IriusRisk-branded interface with modern styling

👉 **[📖 GUI Documentation](README_GUI.md)** - Complete web interface guide

### ⚡ **Command Line Interface (For automation & scripting)**
- **Automation-ready**: Perfect for CI/CD pipelines and scheduled tasks
- **Scriptable**: Ideal for enterprise automation and batch processing
- **Lightweight**: No browser required, runs in any terminal
- **Full control**: Individual phase execution and advanced options

👉 **[📖 CLI Documentation](README_CLI.md)** - Complete command-line guide

## 📋 Project Overview

This tool automates the process of collecting, mapping, and transferring risk patterns between component versions, ensuring that deprecated v1 components receive the latest security content from their modern v2 equivalents.

**Why does this exist?**

IriusRisk allows you to switch out components and this feature will allow you to replace a deprecated v1 component for a new v2 component **BUT** it will remove any content for that component fully from project. To facilitate this transfer, this project will help you import the new v2 content onto the existing v1 components across the full tenant. This means that all of your v1 components will now have v2 content side by side your existing v1 content. 

## 🎯 Key Features

### **Core Migration Capabilities**
- ✅ **Component Collection**: Automatically collect v1 and v2 components via API 
- ✅ **Risk Pattern Transfer**: Bulk transfer risk patterns from v2 to v1 components
- ✅ **Cleanup & Testing**: Complete cleanup functionality for repeated testing
- ✅ **Comprehensive Logging**: Full audit trail of all operations
- ✅ **Rate Limiting**: API-friendly with configurable delays
- ✅ **Error Handling**: Robust error handling and recovery

## � Choose Your Interface

This tool provides **two ways** to run the migration process. Choose the interface that best fits your needs:

### 🌐 **Web Interface (Recommended for new users)**
- **Best for**: Interactive use, visual progress tracking, one-time migrations
- **Benefits**: Real-time streaming, point-and-click setup, visual dashboard
- **Documentation**: See [**README_GUI.md**](README_GUI.md) for complete setup and usage

### 💻 **Command Line Interface (Recommended for automation)**
- **Best for**: Automation, CI/CD pipelines, scripting, advanced users
- **Benefits**: Individual phase control, test mode, scriptable operations
- **Documentation**: See [**README_CLI.md**](README_CLI.md) for complete setup and usage

---

## 🚀 Quick Start

### For Web Interface Users:
```bash
# Install and run the web interface
git clone https://github.com/iriusrisk/IriusRisk-Central.git
cd IriusRisk-Central/Integrations/v1_v2_migration_tool
pip install -r requirements.txt
streamlit run app.py
```

### For Command Line Users:
```bash
# Install and run the CLI
git clone https://github.com/iriusrisk/IriusRisk-Central.git
cd IriusRisk-Central/Integrations/v1_v2_migration_tool
pip install -r requirements.txt
python main.py
```

**📋 Prerequisites for both interfaces:**
- Python 3.8+ with virtual environment (recommended)
- IriusRisk API access (both v1 and v2 endpoints)
- Valid user credentials with appropriate permissions

> 💡 **New to this tool?** Start with the **Web Interface** - it provides guided setup and real-time progress tracking!

## � Detailed Documentation

For complete setup, configuration, and usage instructions, please refer to the appropriate guide:

- � **[Web Interface Guide (README_GUI.md)](README_GUI.md)** - Complete Streamlit setup and usage
- � **[Command Line Guide (README_CLI.md)](README_CLI.md)** - CLI setup, automation, and scripting

## ⚙️ How It Works

This tool automates the migration of risk patterns from modern (v2) components to legacy (v1) components in IriusRisk. The migration follows a structured **4-phase approach**:

### 🔄 **Migration Process**

1. **Phase 1**: Collect all deprecated (v1) components from your IriusRisk instance
2. **Phase 2**: Collect all modern (v2) components from your IriusRisk instance  
3. **Phase 4a**: Discover and collect risk patterns attached to v2 components
4. **Phase 4b**: Transfer risk patterns from v2 components to their v1 counterparts

> **Note**: Phase 3 (CSV to JSON conversion) has already been completed - the component mappings are pre-built.

### 📊 **What Gets Migrated**

- ✅ **Risk Patterns**: Security threats, countermeasures, and risk assessments
- ✅ **Component Mappings**: Predefined relationships between v1 and v2 components
- ✅ **Metadata**: Component IDs, names, descriptions, and categorizations
- ✅ **Audit Trail**: Complete logging of all operations and results

### 🔄 **Testing & Cleanup**

The tool includes cleanup functionality for testing environments:
- Transfer risk patterns to test the migration
- Run your validation and testing
- Clean up (remove transferred patterns) to reset the environment
- Repeat the cycle as needed

For detailed phase-by-phase instructions and examples, see the interface-specific documentation above.


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

For detailed troubleshooting guides, configuration help, and common issues:

- 🌐 **Web Interface Issues**: See [README_GUI.md - Troubleshooting](README_GUI.md#troubleshooting)
- 💻 **Command Line Issues**: See [README_CLI.md - Troubleshooting](README_CLI.md#troubleshooting)
- 🐛 **General Issues**: Create an issue in this repository

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎯 Built with ❤️ for IriusRisk component migration | Choose your interface above to get started!**/
