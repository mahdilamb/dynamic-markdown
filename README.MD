# Dynamic markdown

[![Check code quality and run unit tests](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml/badge.svg)](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml)

Python package to enable executing python scripts from within a markdown file.

## Usage

### Installation

```shell
pip install git+https://github.com/mahdilamb/dynamic-markdown
```

Most of the python code is executed as is and can be performed as such:

```shell
dynamic-markdown [--file=blah.MD]
```

If file is not supplied, the package will try and find a `Readme.md.in` or `Readme.md` file (case-insensitive).

Getting and setting:

```markdown
# Test

<!--{% x = 12345 %}-->
<!--{{x}}--><!--{><}-->

```

## Syntax

Processed blocks must be one of the following:

* Control  `<!--{% ... %}-->`
* Capture  `<!--{{ ... }}-->`
* Flush `<!--{> ... <}-->`
* capture and Flush `<!--{{> ... <}}-->`
