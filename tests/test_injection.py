from unittest import mock

from dynamic_markdown import utils

fake_module = type(
    "fake_module",
    (),
    {"get": lambda: 1, "repeat": lambda *_, **__: f"{_}, {__}"},
)


@mock.patch("sys.modules", new={"fake": fake_module})
def injection_works_test():
    """Test that we can inject content."""
    assert (
        utils.inject("<!---{$ fake::get() $}--><!--{><}-->")
        == "<!---{$ fake::get() $}-->1<!--{><}-->"
    )
    assert (
        utils.inject("<!---{$ fake::repeat(a=23) $}--><!--{><}-->")
        == "<!---{$ fake::repeat(a=23) $}-->(), {'a': 23}<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def format_spec_test():
    """Test that format_spec works."""
    assert (
        utils.inject("<!---{$ fake::get() :.2f$}--><!--{><}-->")
        == "<!---{$ fake::get() :.2f$}-->1.00<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def inline_test():
    """Test that we can inject content inline."""
    assert (
        utils.inject("One is <!---{$ fake::get() $}--><!--{><}-->")
        == "One is <!---{$ fake::get() $}-->1<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def newline_test():
    """Test that we can inject content when it happens in a block."""
    assert (
        utils.inject(
            """One is:
<!---{$ fake::get() $}--><!--{><}-->"""
        )
        == """One is:
<!---{$ fake::get() $}-->1<!--{><}-->"""
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def replacement_test():
    """Check that we can replace content."""
    assert (
        utils.inject("One is <!---{$ fake::get() $}-->2<!--{><}-->.")
        == "One is <!---{$ fake::get() $}-->1<!--{><}-->."
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def multiple_replacement_test():
    """Test that multiple replacements work."""
    assert (
        utils.inject(
            "One is <!---{$ fake::get() $}--><!--{><}-->. Une is <!---{$ fake::get() $}--><!--{><}-->. Uno is <!---{$ fake::get() $}--><!--{><}-->."
        )
        == "One is <!---{$ fake::get() $}-->1<!--{><}-->. Une is <!---{$ fake::get() $}-->1<!--{><}-->. Uno is <!---{$ fake::get() $}-->1<!--{><}-->."
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
