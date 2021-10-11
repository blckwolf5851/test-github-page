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
    table = "<table id=\"table\">\n"
    table += "    <tr>\n        %s\n    </tr>\n" % str("\n        ".join([f"<th>{col}</th>" for col in columns]))
    row_attributes = ["state", "priority", "milestone"]
    for issue in issues:
        issue_id = f"""<td><a href=\"{issue["html_url"]}\">{issue["number"]}</a></td>"""
        title = f"""<td>{issue["title"]}</td>"""
        status = f"""<td>{issue["state"]}</td>"""        
        priority = f"""<td>{issue["priority"]}</td>"""        
        owner = f"""<td>{issue["assignees"]}</td>"""
        blank_status = f"""<td></td>"""
        row = [issue_id, title, status, priority, owner, blank_status]
        attributes = ' '.join([f'{attr}="{issue[attr]}"' for attr in row_attributes])
        table += "    <tr %s>\n        %s\n    </tr>\n" % (attributes, str("\n        ".join(row)))
        # table += f'    <tr {attributes}>\n        {"\n        ".join(row)}\n    </tr>\n'
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
<table id="filter">
  <tr>
      <td>Priority</td>
      <td><input type="text" id="priority" onkeyup="filter()" placeholder="high" title="Priority Filter"></td>
  </tr>
  <tr>
      <td>Milestone</td>
      <td><input type="text" id="milestone" onkeyup="filter()" placeholder="2022.1" title="Milestone Filter"></td>
  </tr>
  <tr>
      <td>Status</td>
      <td><input type="text" id="status" onkeyup="filter()" placeholder="open" title="Status Filter"></td>
  </tr>
</table>

<p></p>
"""
    result += table
    result += """
</body>

<script>
const filter = () => {
  var input, filter, table, tr, td, i;
  priority = document.getElementById("priority").value;
  milestone = document.getElementById("milestone").value;
  state = document.getElementById("status").value;

  table = document.getElementById("table");
  tr = table.getElementsByTagName("tr");

  // Replace space with | to have or condition in regex
  priority = priority.replace(/\s+/g, '|')
  milestone = milestone.replace(/\s+/g, '|')
  state = state.replace(/\s+/g, '|')

  const priority_regex = new RegExp(priority, 'i');
  const milestone_regex = new RegExp(milestone, 'i');
  const state_regex = new RegExp(state, 'i');

  for (i = 0; i < tr.length; i++) {
    // Do not display a row if:
    // 1. it does not contain keywords
    // 2. the filter condition is not empty
    // 3. the original field is not empty
    if (!priority_regex.test(tr[i].getAttribute("priority")) && priority !== "" && tr[i].getAttribute("priority")) {
      tr[i].style.display = "none";
      continue;
    }
    if (!milestone_regex.test(tr[i].getAttribute("milestone")) && milestone !== "" && tr[i].getAttribute("milestone")) {
      tr[i].style.display = "none";
      continue;
    }
    if (!state_regex.test(tr[i].getAttribute("state")) && state !== "" && tr[i].getAttribute("state")) {
      tr[i].style.display = "none";
      continue;
    }
    tr[i].style.display = ""; 
  }
  // Do not hide the headers
  tr[0].style.display = ""; 
};
</script>
</html>
"""
    return result

columns = ["id", "title", "status", "priority", "owner", "status"]
issues = [compress_issue(issue) for issue in issues if keep_issue(issue)]
print(array2htmltable(columns, issues))
# print(json.dumps(issues, indent=4))