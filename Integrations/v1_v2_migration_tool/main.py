#!/usr/bin/env python3
"""
Main Orchestrator

This script runs the complete component migration process sequentially:
1. Phase 1: Collect v1 (deprecated) components
2. Phase 2: Collect v2 (modern) components  
3. Phase 4a: Collect risk patterns from v2 components
4. Phase 4b: Transfer risk patterns to v1 components

Prerequisites:
- v1_v2_component_mappings.json file must exist
- .env file with API_TOKEN, SUBDOMAIN, and OPENAI_API_KEY
"""

import sys
import os
import subprocess
import time
import json
from datetime import datetime

# Add src directory to path so we can import our modules
sys.path.append('src')

def print_banner():
    """Print the Radiant Swing banner"""
    print("=" * 60)
    print("🌅 RADIANT SWING - Component Migration System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_phase_banner(phase_num, phase_name):
    """Print a phase banner"""
    print("\n" + "=" * 50)
    print(f"📋 Phase {phase_num}: {phase_name}")
    print("=" * 50)

def check_prerequisites():
    """Check that all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check for v1_v2_component_mappings.json
    if not os.path.exists('v1_v2_component_mappings.json'):
        print("❌ Error: v1_v2_component_mappings.json not found")
        print("   Please ensure this file exists before running the migration")
        return False
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        print("   Please create .env with API_TOKEN, SUBDOMAIN, and OPENAI_API_KEY")
        return False
    
    # Check src directory exists
    if not os.path.exists('src'):
        print("❌ Error: src directory not found")
        return False
    
    # Check that required Python files exist
    required_files = [
        'src/phase1_collect_v1_components.py',
        'src/phase2_collect_v2_components.py', 
        'src/phase4a_collect_risk_patterns.py',
        'src/phase4b_transfer_risk_patterns.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Error: {file_path} not found")
            return False
    
    # Load and validate mappings file
    try:
        with open('v1_v2_component_mappings.json', 'r') as f:
            mappings = json.load(f)
        print(f"✅ Found {len(mappings)} component mappings")
    except Exception as e:
        print(f"❌ Error reading v1_v2_component_mappings.json: {e}")
        return False
    
    print("✅ All prerequisites met!")
    return True

def run_phase(phase_script, phase_name, phase_num):
    """Run a phase script and handle the results"""
    return run_phase_with_args([phase_script], phase_name, phase_num)

def run_phase_with_args(phase_args, phase_name, phase_num):
    """Run a phase script with arguments and handle the results"""
    print_phase_banner(phase_num, phase_name)
    print(f"🚀 Starting Phase {phase_num} at {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Debug: Show what we're running and where
        cmd = [sys.executable] + phase_args
        working_dir = os.getcwd()
        print(f"🔧 Command: {' '.join(cmd)}")
        print(f"🔧 Working directory: {working_dir}")
        
        # Run the phase script with real-time output
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            # Don't capture output - let it stream to console in real-time
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ Phase {phase_num} completed successfully in {elapsed_time:.2f} seconds at {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"\n❌ Phase {phase_num} failed at {datetime.now().strftime('%H:%M:%S')} (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running Phase {phase_num}: {e}")
        return False
    
    return True

def print_summary():
    """Print a summary of generated files"""
    print("\n" + "=" * 50)
    print("📊 MIGRATION SUMMARY")
    print("=" * 50)
    
    files_to_check = [
        ('v1_components.json', 'V1 (deprecated) components'),
        ('v2_components.json', 'V2 (modern) components'),
        ('matching_risk_patterns.json', 'Risk patterns collected'),
        ('phase4b_transfer_results.json', 'Transfer results'),
        ('action.log', 'Action log')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        print(f"✅ {description}: {len(data)} items")
                    else:
                        print(f"✅ {description}: Generated")
                else:
                    # For log files, just check they exist
                    print(f"✅ {description}: Generated")
            except:
                print(f"⚠️  {description}: File exists but couldn't read details")
        else:
            print(f"❌ {description}: Not found")

def main():
    """Main orchestrator function"""
    print_banner()
    
    # Check if this is a test run
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    if test_mode:
        print("🧪 Running in TEST MODE - Limited processing for faster execution")
        print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Exiting.")
        sys.exit(1)
    
    # Phase 1: Collect V1 Components
    if not run_phase('src/phase1_collect_v1_components.py', 'Collect V1 Components', '1'):
        print("\n❌ Phase 1 failed. Stopping execution.")
        sys.exit(1)
    
    # Small delay between phases
    time.sleep(2)
    
    # Phase 2: Collect V2 Components  
    if not run_phase('src/phase2_collect_v2_components.py', 'Collect V2 Components', '2'):
        print("\n❌ Phase 2 failed. Stopping execution.")
        sys.exit(1)
    
    # Small delay between phases
    time.sleep(2)
    
    # Phase 4a: Collect Risk Patterns
    phase4a_args = ['src/phase4a_collect_risk_patterns.py']
    if test_mode:
        phase4a_args.append('--test')
    if not run_phase_with_args(phase4a_args, 'Collect Risk Patterns', '4a'):
        print("\n❌ Phase 4a failed. Stopping execution.")
        sys.exit(1)
    
    # Small delay between phases
    time.sleep(2)
    
    # Phase 4b: Transfer Risk Patterns
    if not run_phase('src/phase4b_transfer_risk_patterns.py', 'Transfer Risk Patterns', '4b'):
        print("\n❌ Phase 4b failed. Stopping execution.")
        sys.exit(1)
    
    # Print final summary
    print_summary()
    
    print("\n" + "=" * 60)
    print("🎉 RADIANT SWING MIGRATION COMPLETE!")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()