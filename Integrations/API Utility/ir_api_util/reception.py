import os
import subprocess

class Reception:
    print("")
    def __init__(self):
        self.menu = ["Main Menu:", "", "1. Get Project List", "2. Export IR Project Status","9. Exit"]
        self.menuSelection = 0

    def main_menu(self):
        for item in self.menu:
            print(item)

    def execute_script(self, script_path, args):
        script_absolute_path = os.path.expanduser(script_path)
        try:
            subprocess.run(['python3', script_absolute_path] + args, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {script_absolute_path}, {e}")

    def execute_script_noArgs(self, script_path):
        script_absolute_path = os.path.expanduser(script_path)
        try:
            subprocess.run(['python3', script_absolute_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {script_absolute_path}, {e}")

    def main(self):
        while True:
            self.main_menu()
            print("")
            choice = input("Please make a selection: ")
            print("")
            if choice == "1":
                self.execute_script_noArgs('~/ir_api_util/getProjectList.py')
            elif choice == "2":
                project_id = input("Enter the target Project ID: ")
                print("")
                self.execute_script('~/ir_api_util/getProject_CM_Status.py', [project_id])
            elif choice == "9":
                print("Exiting")
                break
            else:
                print("Invalid Selection. Please try again.")
