from flask import Flask, render_template_string, request
import importlib
import logging

app = Flask(__name__)

# Define the scripts you want to run
SCRIPTS = {
    "Security Classifications": "tenant_config_migration_security_classifications",
    "Trust Zones": "tenant_config_migration_trust_zones",
    "Workflows": "tenant_config_migration_workflows",
    "Permissions": "tenant_config_migration_permissions",
    "Custom Fields": "tenant_config_migration_customfields",
    "Business Units": "tenant_config_migration_BUs",
    "Assets": "tenant_config_migration_assets",
    "Components": "tenant_config_migration_components",
    "Libraries": "tenant_config_migration_libraries",

}

index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Script Runner</title>
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.css">
</head>
<body>
    <h1>Run Scripts</h1>
    <form method="post" action="{{ url_for('run_script') }}">
        <label for="script">Select Script:</label>
        <select id="script" name="script">
            {% for script_name in scripts %}
                <option value="{{ script_name }}">{{ script_name }}</option>
            {% endfor %}
        </select>
        <br>
        <label for="source_domain">Source Domain:</label>
        <input type="text" id="source_domain" name="source_domain" required>
        <br>
        <label for="dest_domain">Destination Domain:</label>
        <input type="text" id="dest_domain" name="dest_domain" required>
        <br>
        <label for="source_api_token">Source API Token:</label>
        <input type="text" id="source_api_token" name="source_api_token" required>
        <br>
        <label for="dest_api_token">Destination API Token:</label>
        <input type="text" id="dest_api_token" name="dest_api_token" required>
        <br>
        <button type="submit">Run</button>
    </form>
    {% if output %}
        <h2>Output:</h2>
        <pre>{{ output }}</pre>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(index_html, scripts=SCRIPTS)

@app.route('/run_script', methods=['POST'])
def run_script():
    script_name = request.form['script']
    script_module = SCRIPTS.get(script_name)
    source_domain = request.form['source_domain']
    dest_domain = request.form['dest_domain']
    source_api_token = request.form['source_api_token']
    dest_api_token = request.form['dest_api_token']
    
    if script_module:
        try:
            module = importlib.import_module(script_module)
            if hasattr(module, 'main'):
                result = module.main(source_domain, dest_domain, build_headers(source_api_token), build_headers(dest_api_token))
                output = f"Script {script_name} executed successfully.\n{result}"
            else:
                output = f"Script {script_name} does not have a main function."
        except Exception as e:
            logging.error(f"Error running script {script_name}: {e}")
            output = f"An error occurred while running the script:\n{str(e)}"
    else:
        output = f"Script {script_name} not found."
    
    return render_template_string(index_html, scripts=SCRIPTS, output=output)

def build_headers(api_token):
    return {
        "api-token": api_token
    }

if __name__ == '__main__':
    app.run(debug=True)