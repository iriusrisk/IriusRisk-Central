import subprocess
import sys
import os
import json
import threading
import queue
from datetime import datetime
from pathlib import Path

class MigrationRunner:
    """Handle the migration process execution and monitoring"""
    
    def __init__(self, log_file: str = "migration.log"):
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False
        self.log_file = log_file
        
    def _log_to_file(self, message: str):
        """Write a message to the log file with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Warning: Could not write to log file {self.log_file}: {e}")
        
    def check_prerequisites(self):
        """Check that all prerequisites are met"""
        issues = []
        
        # Check for v1_v2_component_mappings.json
        if not os.path.exists('v1_v2_component_mappings.json'):
            issues.append("❌ v1_v2_component_mappings.json not found")
        
        # Check src directory exists
        if not os.path.exists('src'):
            issues.append("❌ src directory not found")
        
        # Check that required Python files exist
        required_files = [
            'src/phase1_collect_v1_components.py',
            'src/phase2_collect_v2_components.py', 
            'src/phase4a_collect_risk_patterns.py',
            'src/phase4b_transfer_risk_patterns.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                issues.append(f"❌ {file_path} not found")
        
        return issues
    
    def _enqueue_output(self, stdout, queue):
        """Put subprocess output into queue and log to file"""
        try:
            for line in iter(stdout.readline, ''):
                if line:  # Only add non-empty lines
                    cleaned_line = line.rstrip()
                    if cleaned_line:  # Only add non-empty after stripping
                        queue.put(cleaned_line)
                        self._log_to_file(cleaned_line)  # Also log to file
        except Exception as e:
            error_msg = f"Error reading output: {e}"
            queue.put(error_msg)
            self._log_to_file(error_msg)
        finally:
            if stdout:
                stdout.close()
    
    def start_migration(self, test_mode: bool = False):
        """Start the migration process"""
        if self.is_running:
            return False, "Migration is already running"
        
        try:
            # Prepare command
            cmd = [sys.executable, 'main.py']
            if test_mode:
                cmd.append('--test')
            
            # Log migration start
            start_msg = f"Starting migration with command: {' '.join(cmd)}"
            if test_mode:
                start_msg += " (TEST MODE)"
            self._log_to_file(start_msg)
            self._log_to_file("=" * 60)
            
            # Clear previous output
            while not self.output_queue.empty():
                try:
                    self.output_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Start process with unbuffered output
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=0,  # Unbuffered
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force Python to be unbuffered
            )
            
            # Start thread to read output
            output_thread = threading.Thread(
                target=self._enqueue_output,
                args=(self.process.stdout, self.output_queue)
            )
            output_thread.daemon = True
            output_thread.start()
            
            self.is_running = True
            success_msg = f"Migration started at {datetime.now().strftime('%H:%M:%S')}"
            self._log_to_file(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error starting migration: {str(e)}"
            self._log_to_file(error_msg)
            return False, error_msg
    
    def get_output_lines(self):
        """Get new output lines from the migration process"""
        lines = []
        try:
            while True:
                line = self.output_queue.get_nowait()
                lines.append(line)
        except queue.Empty:
            pass
        return lines
    
    def is_process_running(self):
        """Check if the migration process is still running"""
        if not self.is_running or not self.process:
            return False
        
        if self.process.poll() is None:
            return True
        else:
            self.is_running = False
            return False
    
    def get_process_result(self):
        """Get the final result of the migration process"""
        if self.process and self.process.poll() is not None:
            return_code = self.process.returncode
            if return_code == 0:
                success_msg = f"Migration completed successfully at {datetime.now().strftime('%H:%M:%S')}"
                self._log_to_file(success_msg)
                self._log_to_file("=" * 60)
                return True, success_msg
            else:
                error_msg = f"Migration failed with exit code: {return_code}"
                self._log_to_file(error_msg)
                self._log_to_file("=" * 60)
                return False, error_msg
        return None, None
    
    def stop_migration(self):
        """Stop the migration process"""
        if self.process and self.is_running:
            stop_msg = f"Migration stopped by user at {datetime.now().strftime('%H:%M:%S')}"
            self._log_to_file(stop_msg)
            self._log_to_file("=" * 60)
            self.process.terminate()
            self.is_running = False
            return True
        return False
    
    def get_log_content(self, max_lines: int = 1000):
        """Get the content of the migration log file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Return last max_lines
                    return ''.join(lines[-max_lines:])
            return "No log file found"
        except Exception as e:
            return f"Error reading log file: {e}"
    
    def clear_log(self):
        """Clear the migration log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file cleared\n")
            return True
        except Exception as e:
            print(f"Error clearing log file: {e}")
            return False

def get_migration_summary():
    """Get summary of generated files"""
    files_to_check = [
        ('v1_components.json', 'V1 (deprecated) components'),
        ('v2_components.json', 'V2 (modern) components'),
        ('matching_risk_patterns.json', 'Risk patterns collected'),
        ('phase4b_transfer_results.json', 'Transfer results'),
        ('migration.log', 'Migration process log'),
        ('action.log', 'Action log')
    ]
    
    summary = []
    for filename, description in files_to_check:
        if os.path.exists(filename):
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        summary.append(f"✅ {description}: {len(data)} items")
                    else:
                        summary.append(f"✅ {description}: Generated")
                else:
                    summary.append(f"✅ {description}: Generated")
            except:
                summary.append(f"⚠️  {description}: File exists but couldn't read details")
        else:
            summary.append(f"❌ {description}: Not found")
    
    return summary

def save_env_variables(api_token: str, subdomain: str):
    """Save API token and subdomain to .env file"""
    env_content = f"API_TOKEN={api_token}\nSUBDOMAIN={subdomain}\n"
    with open('.env', 'w') as f:
        f.write(env_content)

def load_env_variables():
    """Load existing API token and subdomain from .env file"""
    if os.path.exists('.env'):
        env_vars = {}
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
        return env_vars.get('API_TOKEN', ''), env_vars.get('SUBDOMAIN', '')
    return '', ''