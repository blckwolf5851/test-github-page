# Example usage: python .\parse_coverage.py child_build parent_build
import xml.etree.ElementTree as ET
import sys
import argparse
import json

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('json_file', type=str,
                    help='json file containing all issues')
args = parser.parse_args()

with open(args.json_file, 'r') as f:
    issues = json.load(f)

def keep_issue(issue):
    return "pull_request" not in issue

def compress_issue(issue):
    field_to_keep = ["number", "html_url", "title", "assignees", "milestone", "state", "labels"]
    issue = {field:issue[field] for field in field_to_keep}
    issue["labels"] = [label["name"] for label in issue["labels"]]
    issue["assignees"] = ','.join([user["login"] for user in issue["assignees"]])
    issue["priority"] = ""
    for label in issue["labels"]:
        if label.startswith('priority'):
            issue["priority"] = label.split(":")[1]
            break
    return issue


def array2htmltable(columns, issues):
    table = "<table>\n"
    table += "    <tr>\n        %s\n    </tr>\n" % str("\n        ".join([f"<th>{col}</th>" for col in columns]))
    for issue in issues:
        issue_id = f"""<td><a href=\"{issue["html_url"]}\">{issue["number"]}</a></td>"""
        title = f"""<td>{issue["title"]}</td>"""
        status = f"""<td>{issue["state"]}</td>"""        
        priority = f"""<td>{issue["priority"]}</td>"""        
        owner = f"""<td>{issue["assignees"]}</td>"""
        blank_status = f"""<td></td>"""
        row = [issue_id, title, status, priority, owner, blank_status]
        table += "    <tr>\n        %s\n    </tr>\n" % str("\n        ".join(row))
    table += "</table>"
    result = """<!DOCTYPE html>
<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #616161;
  text-align: left;
  padding: 8px;
}

th {
  background-color: #0153a0;
  color: #ffffff;
}

tr:nth-child(even) {
  background-color: #ddecfa;
}
</style>
</head>
<body>
"""
    result += table
    result += """
</body>
</html>
"""
    return result

columns = ["id", "title", "status", "priority", "owner", "status"]
issues = [compress_issue(issue) for issue in issues if keep_issue(issue)]
print(array2htmltable(columns, issues))
# print(json.dumps(issues, indent=4))