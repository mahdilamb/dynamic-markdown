from unittest import mock

from dynamic_markdown import processor

fake_module = type(
    "fake_module",
    (),
    {"get": lambda: 1, "repeat": lambda *_, **__: f"{_}, {__}"},
)


@mock.patch("sys.modules", new={"fake": fake_module})
def injection_works_test():
    """Test that we can inject content."""
    assert (
        processor.process("<!---{$ a = fake:get() $}--><!--{{a}}--><!--{><}-->")
        == "<!---{$ a = fake:get() $}--><!--{{a}}-->1<!--{><}-->"
    )
    assert (
        processor.process("<!---{$ a = fake:repeat(a=23) $}--><!--{{a}}--><!--{><}-->")
        == "<!---{$ a = fake:repeat(a=23) $}--><!--{{a}}-->(), {'a': 23}<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def format_spec_test():
    """Test that format_spec works."""
    assert (
        processor.process("<!---{$ b = fake:get() $}--><!--{{b:.2f}}--><!--{><}-->")
        == "<!---{$ b = fake:get() $}--><!--{{b:.2f}}-->1.00<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def inline_test():
    """Test that we can inject content inline."""
    assert (
        processor.process("One is <!---{$ c = fake:get() $}--><!--{{c}}--><!--{><}-->")
        == "One is <!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def newline_test():
    """Test that we can inject content when it happens in a block."""
    assert (
        processor.process(
            """One is:
<!---{$ c = fake:get() $}--><!--{{c}}--><!--{><}-->"""
        )
        == """One is:
<!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->"""
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def replacement_test():
    """Check that we can replace content."""
    assert (
        processor.process(
            "One is <!---{$ c = fake:get() $}--><!--{{c}}-->1234<!--{><}-->."
        )
        == "One is <!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->."
    )


@mock.patch("sys.modules", new={"fake": fake_module})
def multiple_replacement_test():
    """Test that multiple replacements work."""
    assert (
        processor.process(
            "One is <!---{$ c = fake:get() $}--><!--{{c}}--><!--{><}-->. Une is <!---{$ c = fake:get() $}--><!--{{c}}--><!--{><}-->. Uno is <!---{$ c = fake:get() $}--><!--{{c}}--><!--{><}-->."
        )
        == "One is <!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->. Une is <!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->. Uno is <!---{$ c = fake:get() $}--><!--{{c}}-->1<!--{><}-->."
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
