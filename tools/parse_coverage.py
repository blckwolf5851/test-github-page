# Example usage: python .\parse_coverage.py child_build parent_build
import xml.etree.ElementTree as ET
import sys
import argparse
import glob

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('child_coverage', type=str,
                    help='Child branch build directory')
parser.add_argument('parent_coverage', type=str,
                    help='Parent branch build directory')
args = parser.parse_args()

child_cov_file = glob.glob(args.child_coverage + "/Testing/**/Coverage.xml", recursive = True)[0]
parent_cov_file = glob.glob(args.parent_coverage + "/Testing/**/Coverage.xml", recursive = True)[0]

def want_file(fn):
    return fn.startswith("./src")

def pprint_table(matrix):
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col))+1 for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))

with open(child_cov_file, 'r') as f:
    child_data = f.read()
with open(parent_cov_file, 'r') as f:
    parent_data = f.read()

# Parse child
child_file_to_coverage = {}
root = ET.fromstring(child_data)
for elm in root.findall(".//File[@FullPath]"):
    fn = elm.attrib["FullPath"]
    if not want_file(fn):
        continue
    percent_cov = float(elm.find('PercentCoverage').text)
    child_file_to_coverage[fn] = percent_cov

# Parse parent
parent_file_to_coverage = {}
root = ET.fromstring(parent_data)
for elm in root.findall(".//File[@FullPath]"):
    fn = elm.attrib["FullPath"]
    if not want_file(fn):
        continue
    percent_cov = float(elm.find('PercentCoverage').text)
    parent_file_to_coverage[fn] = percent_cov

columns = ["File Name", "Coverage (%)", "Delta Coverage"]
separator = ['-'*len(cn) for cn in columns]
result = []
fail = False
coverage_decreased = False
new_file_not_covered = False
for fn in child_file_to_coverage:
    parent_cov = parent_file_to_coverage[fn] if fn in parent_file_to_coverage else 0
    child_cov = child_file_to_coverage[fn]
    delta_cov = child_cov - parent_cov
    result.append([fn, child_cov, delta_cov])
    if fn not in parent_file_to_coverage and delta_cov == 0:
        new_file_not_covered = True
    if delta_cov < 0:
        coverage_decreased = True

result = [columns, separator] + result

if new_file_not_covered:
    pprint_table(result)
    print("New files are not covered")
    exit(1)
elif coverage_decreased:
    pprint_table(result)
    print("Coverage decreased.")
    exit(78)
else:
    pprint_table(result)
    print("Coverage did not decrease.")
    exit(0)
