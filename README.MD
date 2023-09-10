# Dynamic markdown

[![Check code quality and run unit tests](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml/badge.svg)](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml)

Python package for integrating python function results into a markdown document.

# Usage

Function calling:

```markdown
# Function calling

<!--{$ path.to.module::function(1, 2, k='v') $}-->
<!--{><}-->


```

Getting and setting:

```markdown
# Test

<!---{% set x = 12345 %}-->
<!--{{x}}--><!--{><}-->
```

## Syntax

Processed blocks must be one of the following:

* Function calls `<!--{$ ... $}-->`
* Control calls `<!--{% ... %}-->`
* Output calls `<!--{{ ... }}-->`
* Flush `<!--{> ... <}-->`
