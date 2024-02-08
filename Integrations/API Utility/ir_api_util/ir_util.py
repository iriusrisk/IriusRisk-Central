import os
from reception import Reception
from auth import Auth
from health import Health

if __name__ == "__main__":
    instance_file_path = os.path.expanduser("~/ir/ir_instance_domain")
    token_file_path = os.path.expanduser("~/ir/.ir_user_token")

    auth = Auth()
    auth.check_user_instance_file(instance_file_path)
    auth.check_user_token_file(token_file_path)

    health = Health(instance_file_path)
    if health.test_api_health():
        reception = Reception()
        reception.main()
    else:
        print("Exiting due to failed API health check.")
