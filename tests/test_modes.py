"""Tests for the different modes."""
from dynamic_markdown import processor


def finalize_multiline_test():
    """Test stripping whitespace from multiline."""
    assert (
        processor.process(
            r"""Prefix

<!--{{1}}-->
    <!--{{2}}-->
<!--{{3}}-->

Postfix""",
            mode="finalize",
        )
        == r"""Prefix

Postfix"""
    )


def finalize_inline_test():
    """Test stripping whitespace from inline usage."""
    assert (
        processor.process(
            r"""Prefix: <!--{{1}}--> .""",
            mode="finalize",
        )
        == r"""Prefix:  ."""
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(sys.argv + ["-vv", "-s"]))
