# tlparser

[![PyPI](https://img.shields.io/pypi/v/tlparser.svg)](https://pypi.org/project/tlparser/)
[![Changelog](https://img.shields.io/github/v/release/RomanBoegli/tlparser?include_prereleases&label=changelog)](https://github.com/RomanBoegli/tlparser/releases)
[![Tests](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml/badge.svg)](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/RomanBoegli/tlparser/blob/master/LICENSE)

Temporal Logic Parser

## Installation

Install this tool using `pip`:
```bash
pip install tlparser
```
## Usage

For help, run:
```bash
tlparser --help
```
You can also use:
```bash
python -m tlparser --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd tlparser
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
