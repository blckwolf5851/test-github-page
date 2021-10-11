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
    field_to_keep = ["number", "url", "title", "assignee", "assignees", "milestone", "state", "labels"]
    return {field:issue[field] for field in field_to_keep}

issues = [compress_issue(issue) for issue in issues if keep_issue(issue)]
print(issues)