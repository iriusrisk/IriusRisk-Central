import os

class Auth:

    def __init__(self):
        pass

    def check_user_instance_file(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file_path):
            print("\nCould not find your IR domain file.")
            user_input = input("Please enter your IR domain: ")
            with open(file_path, 'w') as file:
                file.write(user_input)

    def check_user_token_file(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file_path):
            print("\nCould not find your IR token file.")
            user_input = input("Please enter your API token: ")
            print("")
            with open(file_path, 'w') as file:
                file.write(user_input)
