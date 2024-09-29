# Temporal Logic Parser (`tlparser`)

[![PyPI](https://img.shields.io/pypi/v/tlparser.svg)](https://pypi.org/project/tlparser/)
[![Changelog](https://img.shields.io/github/v/release/RomanBoegli/tlparser?include_prereleases&label=changelog)](https://github.com/RomanBoegli/tlparser/releases)
[![Test](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml/badge.svg)](https://github.com/RomanBoegli/tlparser/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/RomanBoegli/tlparser/blob/master/LICENSE)

Takes something like this as input:

```python
"G((x and (u == 9) and (i < 3)) --> G(not y or x))"
```

And returns some statistics about it, which can be used to derive a statement about the formula's complexity:

tbd
<!-- 
```json
{ 'AST_height': 5,
  'A_n': 0,
  'E_n': 0,
  'F_n': 0,
  'G_n': 2,
  'R_n': 0,
  'U_n': 0,
  'X_n': 0,
  'agg': {'ap': 4, 'cops': 2, 'lops': 5, 'tops': 2},
  'and_n': 2,
  'ap': {'y', 'i_lt_3', 'x', 'u_eq_9'},
  'cops': {'eq': 1, 'geq': 0, 'gt': 0, 'leq': 0, 'lt': 1, 'neq': 0},
  'impl_n': 1,
  'not_n': 1,
  'or_n': 1
}
```

The table below describes the meaning for each value:

Value | Meaning
------|---------
`ap` | Set of all atomic propositions
`AST_height` | Height (or *depth* or *nesting*) of the abstract syntax tree
`A_n` | Not sure actually, something CTL-related? yes 🚧
`E_n` | Not sure actually, something CTL-related? yes 🚧
`F_n` | Number of `eventually` (diamond symbol) operators
`G_n` | Number of `globally` (square symbol) operators
`R_n` | Number of `release`operators
`U_n` | Number of `until`operators
`X_n` | Number of `next`operators
`agg.ap` | Total number of atomic propositions
`agg.cops` | Total number of comparison operators (`==`, `!=`, `<`, `>`, `=>`, `<=`)
`agg.lops` | Total number of logical operators (`and`, `or`, `->`, `not`)
`agg.tops` | Total number of temporal operators (`A`, `E`, `F`, `G`, `R`, `U`, `X`)
`and_n` | Number of `∧` (and) operators (aggregated in `agg.cops`)
`impl_n` | Number of `->` (implies) operators (aggregated in `agg.cops`)
`not_n` | Number of `¬` (not) operators (aggregated in `agg.cops`)
`or_n` | Number of `∨` (or) operators (aggregated in `agg.cops`)
`cops.eq` | Number of equals comparisons (`eq`)
`cops.gt` | Number of greater-than comparisons (`gt`)
`cops.leq` | Number of less-or-equal-than comparisons (`leq`)
`cops.lt` | Number of less-than comparisons (`lt`)
`cops.neq` | Number of non-equals comparisons (`neq`)
-->

<!-- 
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
python3 -m tlparser --help
```
-->

## How to use

To contribute to this tool, first `git clone` this repository and `cd` into the folder.

> [!NOTE]  
> This tool requires **Python 3.10 or later**. Ensure you have the correct version installed. Download it here: [Download Python](https://www.python.org/downloads/)

Next, create a new virtual environment using the following commands:

```bash
python3 -m venv venv && source venv/bin/activate
```

Install and test the dependencies:

```bash
pip3 install --upgrade pip && pip3 install -e '.[test]' && python3 -m pytest
```

Now you are ready to start the `tlparser`.
Test it by printing the `help` message.

```bash
tlparser --help
```

<details>
<summary>Read and plot test data</summary>

First, digest the test data file to create an Excel file.

```bash
tlparser digest ../tlparser/tests/data/test.json
```

The Excel file will serve as basis for generating the plots.

```bash
tlparser visualize -l -p all
```

</details>
</br>

You can parse the `spacewire` requirements using the following command:

```bash
tlparser digest ../tlparser/data/spacewire.json
```

The resulting Excel file serves as basis for generating the plots.

```bash
tlparser visualize -l -p all
```

Exit the virtual environment again using this command:

```bash
deactivate
```
