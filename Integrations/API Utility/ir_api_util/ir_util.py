import os
from reception import Reception
from auth import Auth
from health import Health

if __name__ == "__main__":
    print("Starting script execution.")
    
    instance_file_path = os.path.expanduser("~/ir/ir_instance_domain")
    print(f"Instance file path: {instance_file_path}")
    
    token_file_path = os.path.expanduser("~/ir/.ir_user_token")
    print(f"Token file path: {token_file_path}")

    print("Initializing Auth class.")
    auth = Auth()
    
    print("Checking user instance file.")
    auth.check_user_instance_file(instance_file_path)
    
    print("Checking user token file.")
    auth.check_user_token_file(token_file_path)

    print("Initializing Health class.")
    health = Health(instance_file_path)
    
    print("Testing API health.")
    if health.test_api_health():
        print("API health check passed.")
        
        print("Initializing Reception class.")
        reception = Reception()
        
        print("Executing Reception main method.")
        print("")
        reception.main()
    else:
        print("Exiting due to failed API health check.")
