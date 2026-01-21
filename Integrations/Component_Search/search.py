import requests
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("IRIUSRISK_DOMAIN")
API_TOKEN = os.getenv("IRIUSRISK_API_TOKEN")

if not BASE_URL or not API_TOKEN:
    raise ValueError("IRIUSRISK_DOMAIN and IRIUSRISK_API_TOKEN must be set in .env file")

HEADERS = {
    "API-token": API_TOKEN,
    "Accept": "application/hal+json",
}

def get_all_pages(url, params=None):
    params = dict(params or {})
    page = 0
    size = params.get("size", 100)

    items = []
    while True:
        params.update({"page": page, "size": size})
        r = requests.get(url, headers=HEADERS, params=params, timeout=60)

        if r.status_code == 401:
            raise RuntimeError(
                f"401 Unauthorized\nURL: {r.url}\nBody: {r.text}"
            )

        r.raise_for_status()
        data = r.json()

        page_items = data.get("_embedded", {}).get("items", [])
        items.extend(page_items)

        page_info = data.get("page", {})
        if page >= page_info.get("totalPages", 1) - 1:
            break

        page += 1

    return items

# Parse command line arguments
parser = argparse.ArgumentParser(description="Search for components in IriusRisk and find associated projects")
parser.add_argument("--search", required=True, help="Search term to find in component names or descriptions")
args = parser.parse_args()

search_term = args.search

# Create output filename with current date and search term
current_date = datetime.now().strftime("%Y%m%d")
output_filename = f"{current_date}_{search_term}.txt"

# Open file for writing
with open(output_filename, "w") as output_file:
    # 1) Find components containing the search term (case-insensitive)
    components = get_all_pages(
        f"{BASE_URL}/api/v2/components",
        params={"filter": f"('name'~'{search_term}':OR:'description'~'{search_term}')", "size": 100},
    )

    # Categorize components by match type
    search_lower = search_term.lower()
    name_matches = []
    desc_matches = []
    both_matches = []
    
    for c in components:
        cname = c.get("name", "")
        cdesc = c.get("description", "") or ""
        
        name_match = search_lower in cname.lower()
        desc_match = search_lower in cdesc.lower()
        
        # Get projects for this component
        projects = get_all_pages(
            f"{BASE_URL}/api/v2/components/{c['id']}/projects",
            params={"size": 100},
        )
        
        # Only include components that have projects
        if projects:
            component_info = {
                "component": c,
                "projects": projects
            }
            
            if name_match and desc_match:
                both_matches.append(component_info)
            elif name_match:
                name_matches.append(component_info)
            elif desc_match:
                desc_matches.append(component_info)
    
    def write_output(text):
        """Helper to write to both console and file"""
        print(text)
        output_file.write(text + "\n")
    
    # Display results grouped by match type
    total_components = len(name_matches) + len(desc_matches) + len(both_matches)
    write_output(f"Search Results for '{search_term}': {total_components} component(s) found with projects\n")
    write_output("=" * 80 + "\n")
    
    # Group 1: Matched in Name Only
    if name_matches:
        write_output(f"MATCHED IN NAME ONLY ({len(name_matches)} component(s)):")
        write_output("-" * 80)
        for item in name_matches:
            c = item["component"]
            projects = item["projects"]
            write_output(f"{c.get('name')} | {c['id']} | projects={len(projects)}")
            for p in projects:
                write_output(f"  - {p.get('name')} | {p.get('id')}")
            write_output("")
    
    # Group 2: Matched in Description Only
    if desc_matches:
        write_output(f"MATCHED IN DESCRIPTION ONLY ({len(desc_matches)} component(s)):")
        write_output("-" * 80)
        for item in desc_matches:
            c = item["component"]
            projects = item["projects"]
            cdesc = c.get("description", "")
            desc_snippet = cdesc[:100] + "..." if len(cdesc) > 100 else cdesc
            
            write_output(f"{c.get('name')} | {c['id']} | projects={len(projects)}")
            write_output(f"  Description: {desc_snippet}")
            for p in projects:
                write_output(f"  - {p.get('name')} | {p.get('id')}")
            write_output("")
    
    # Group 3: Matched in Both
    if both_matches:
        write_output(f"MATCHED IN BOTH NAME AND DESCRIPTION ({len(both_matches)} component(s)):")
        write_output("-" * 80)
        for item in both_matches:
            c = item["component"]
            projects = item["projects"]
            write_output(f"{c.get('name')} | {c['id']} | projects={len(projects)}")
            for p in projects:
                write_output(f"  - {p.get('name')} | {p.get('id')}")
            write_output("")

print(f"\nResults saved to: {output_filename}")
