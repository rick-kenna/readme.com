# Create a ReadMe changelog entry.
# The YAML file format is compatible with the rdme script provided by ReadMe.com.

import sys
import json
import yaml
import requests
from base64 import b64encode

def print_help():
    print("Two forms:")
    print(f"  {sys.argv[0]} <title> <type> <body>")
    print(f"  {sys.argv[0]} -f <yaml file name>")
    sys.exit(1)

# Authorization token: we need to base 64 encode it 
# and then decode it to acsii as python 3 stores it as a byte string
# From: https://stackoverflow.com/questions/6999565/python-https-get-with-basic-authentication
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ISO-8859-1")
    print(f"token: {token}")
    return f"Basic {token}"

# Gets the ReadMe version information.
def get_readme_version(base_url, headers, version_id):
    get_version_url = f"{base_url}v1/version/{version_id}"

    resp = requests.get(get_version_url, headers=headers)
    if resp.status_code != 200:
        print(f"Get Version Info error: {get_version_url}: {resp.status_code}, {resp.text}")
        sys.exit(1)

    return resp.json()

# Creates a changelog entry.
def create_changelog(base_url, headers, title, type, body):
    create_log_url = f"{base_url}v1/changelogs"

    if title == "" or type == "" or body == "":
        print(f"Invalid values for: (title, type, body): ({title}, {type}, {body})")
        sys.exit(1)

    # Check for valid `type` values.
    valid_types = ["added", "fixed", "improved", "deprecated", "removed"]
    if not type in valid_types:
        print(f"'type' is not a valid value, {type}.")
        print(f"Valid values are: {valid_types}")
        sys.exit(1)

    changelog_body = { 'title': title,
                       'type': type,
                       'body': body,
                       'hidden': False
                     }

    resp = requests.post(create_log_url, headers=headers, data=json.dumps(changelog_body))
    if resp.status_code != 201:
        print(f"Create Changelog error: {create_log_url}: {resp.status_code}, {resp.text}")
        sys.exit(1)

# Reads the YAML file that should contain: title, type, and body.
# ReadMe docs mention FrontMatter: https://jekyllrb.com/docs/front-matter/.
def get_changelog_info(yaml_file_name):
    try:
        with open(yaml_file_name, 'r') as yaml_f:
            changelog_docs = yaml.safe_load_all(yaml_f)
    
            # The assumption is that there is only one changelog document in the file.
            changelog_info = next(changelog_docs)
            if not "title" in changelog_info:
                print(f"'title' is not in {yaml_file_name}.")
                sys.exit(1)
            title = changelog_info['title']
        
            if not "type" in changelog_info:
                print(f"'type' is not in {yaml_file_name}.")
                sys.exit(1)
            type = changelog_info['type']
        
            if not "body" in changelog_info:
                print(f"'body' is not in {yaml_file_name}.")
                sys.exit(1)
            body = changelog_info['body']
    except FileNotFoundError as fnfe:
        print(f"File {yaml_file_name} not found.")
        sys.exit(1)

    return (title, type, body)

if __name__ == "__main__":
    # Initialize changelog info.
    title = ""
    type = ""
    body = ""

    if len(sys.argv) == 3:
        if (sys.argv[1] != "-f"):
            print("'-f' argument required.")
            print_help()
        yaml_file_name = sys.argv[2]
        (title, type, body) = get_changelog_info(yaml_file_name)

    elif len(sys.argv) == 4:
        # Pick up the input parameters.
        title = sys.argv[1]
        type = sys.argv[2]
        body = sys.argv[3]
    else:
        print("Need required input parameters.")
        print_help()

    # OpenAPI project API key and base URL.
    api_key = "rdme_xn8s9heb1bf82c7618d969ed1df14ba2428d496195eeed063a107e397549a62aeeaa8f"
    base_url = "https://dash.readme.com/api/"

    headers = { 'Content-Type': 'application/json; charset=utf-8',
                'Authorization': basic_auth(api_key, ""),
                'X-Risk-Token': api_key
              }

    version_id = "1.0-rick"

    # Obtain some version information.
    version_info = get_readme_version(base_url, headers, version_id)
    vi_clean_version = version_info['version_clean']
    vi_is_hidden = version_info['is_hidden']
    vi_created = version_info['createdAt']
    print(f"Version: {vi_clean_version}  created on: {vi_created}")

    create_changelog(base_url, headers, title, type, body)
