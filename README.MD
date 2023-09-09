# Dynamic markdown

[![Check code quality and run unit tests](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml/badge.svg)](https://github.com/mahdilamb/dynamic-markdown/actions/workflows/code-quality-and-tests.yaml)

Python package for integrating python function results into a markdown document.

# Usage

Function calling:

```markdown
# Function calling

<!--- path.to.module::function(1, 2, k='v') -->

<!--- $::end -->


```

Getting and setting:

```markdown
# Test

<!--- $::set('x', 1243) --><!-- $::end -->
<!-- $::get('x') --><!-- $::end -->
```

Or (to use a set value in a function call):

```markdown
# Test

<!--- $::set("x", 5) --><!-- $::end -->
<!--- module::sum($x, 5) --><!-- $::end -->
```
