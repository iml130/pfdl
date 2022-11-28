# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""A simple script for running pylint programmatically inside the CI."""

# standard libraries
import sys
import subprocess

folder_path = sys.argv[1]
threshold = float(sys.argv[2])
args = "--rcfile=./third_party/styleguide/.pylintrc"

cmd = "pylint " + folder_path + " " + args

text = ""
try:
    out = subprocess.run(
        cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    text = out.stdout.decode("utf-8")
except subprocess.CalledProcessError as err:
    text = err.output.decode("utf-8")

search_str = "Your code has been rated at "
text = text[text.index(search_str) + len(search_str) : len(text)]
lint_score = float(text[0 : text.index("/")])

if lint_score < threshold:
    message = f"Pylint check failed | Score: {lint_score} | Threshold: {threshold}"
    print(message)
    sys.exit(1)

message = f"Pylint check passed | Score: {lint_score} | Threshold: {threshold}"
print(message)
sys.exit(0)
