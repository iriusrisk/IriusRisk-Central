import os
import subprocess

class Reception:
    def __init__(self):
        self.menu = ["Main Menu:", "",
                     "1. Get Project List",
                     "2. Export IR Project Status",
                     "8. User Access Report",
                     "9. Business Unit Reports",
                     "0. Exit"]
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

    def business_unit_reports_menu(self):
        sub_menu = ["Business Unit Reports:", "",
                    "1. By Business Unit",
                    "2. All Business Units",
                    "0. Back to Main Menu"]
        for item in sub_menu:
            print(item)

        print("")
        choice = input("Please make a selection: ")
        print("")

        if choice == "1":
            business_unit_name_or_uuid = input("Enter the Business Unit name or UUID: ")
            print("")
            self.execute_script('~/ir_api_util/singleBusinessUnit_ByProjects_ByUsers.py', [business_unit_name_or_uuid])
        elif choice == "2":
            self.execute_script_noArgs('~/ir_api_util/allBusinessUnits_ByProjects_ByUsers.py')
        elif choice == "0":
            return
        else:
            print("Invalid Selection. Please try again.")
            self.business_unit_reports_menu()

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
            elif choice == "8":
                days = input("Enter the number of days for the User Access Report: ")
                print("")
                self.execute_script('~/ir_api_util/userAccessReport.py', [days])
            elif choice == "9":
                self.business_unit_reports_menu()
            elif choice == "0":
                print("Exiting")
                print("")
                break
            else:
                print("Invalid Selection. Please try again.")

if __name__ == "__main__":
    Reception().main()
