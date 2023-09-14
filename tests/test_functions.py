from unittest import mock

from dynamic_markdown import processor

fake_adder = type("fake_module", (), {"add": lambda x, y: x + y})


def set_and_get_test():
    """Test that we can get and set values."""
    assert (
        processor.process("""<!---{% x = 1243 %}--><!--{{ x }}--><!--{><}-->""")
        == "<!---{% x = 1243 %}--><!--{{ x }}-->1243<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_adder})
def use_global_test():
    assert (
        (
            processor.process(
                """
<!---{% x = 5 %}-->
<!---{$ y = fake:add(x, 5) $}--><!--{{y}}--><!--{><}-->
"""
            )
        )
        == """
<!---{% x = 5 %}-->
<!---{$ y = fake:add(x, 5) $}--><!--{{y}}-->10<!--{><}-->
"""
    )


@mock.patch("sys.modules", new={"fake": fake_adder})
def store_result_test():
    assert (
        (
            processor.process(
                """
<!---{% x = 5 %}-->
<!---{$ y = fake:add(x, 5) $}--><!--{{y}}--><!--{><}-->
"""
            )
        )
        == """
<!---{% x = 5 %}-->
<!---{$ y = fake:add(x, 5) $}--><!--{{y}}-->10<!--{><}-->
"""
    )


def inline_assignment_test():
    """Test that inline assignment works from a primitive."""
    assert (
        processor.process("""<!--{% df = 123 %}--><!--{{ df }}--><!--{><}-->""")
        == """<!--{% df = 123 %}--><!--{{ df }}-->123<!--{><}-->"""
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
