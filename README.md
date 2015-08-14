# data_wrangler

What is it?
------------
The Jsonifier class entries of personal information in multiple formats and normalizing each entry into a standard JSON format. Valid JSON is written to a file with two-space indentation and keys sorted alphabetically. Entries sorted by lastname, firstname

Usage
------
From command line:
> python jsonifier.py data/data.in

Importing the class:
>>> import jsonifier
>>> j = jsonifier.Jsonifier(data_file='data.in', output_file='result.out')
>>> j.jsonify_data()

Tests
------
For running tests from command line:
> python jsonifier_unittest.py