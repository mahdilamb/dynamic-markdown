from unittest import mock

from dynamic_markdown import utils

fake_adder = type("fake_module", (), {"add": lambda x, y: x + y})


def set_and_get_test():
    """Test that we can get and set values."""
    assert (
        utils.inject("""<!---{% set x = 1243 %}--><!--{{ x }}--><!--{><}-->""")
        == "<!---{% set x = 1243 %}--><!--{{ x }}-->1243<!--{><}-->"
    )


@mock.patch("sys.modules", new={"fake": fake_adder})
def use_global_test():
    assert (
        (
            utils.inject(
                """
<!---{% set x = 5 %}-->
<!---{$ fake::add(x, 5) $}--><!--{><}-->
"""
            )
        )
        == """
<!---{% set x = 5 %}-->
<!---{$ fake::add(x, 5) $}-->10<!--{><}-->
"""
    )


@mock.patch("sys.modules", new={"fake": fake_adder})
def store_result_test():
    assert (
        (
            utils.inject(
                """
<!---{% set x = 5 %}-->
<!---{$ set y= fake::add(x, 5) $}--><!--{{y}}--><!--{><}-->
"""
            )
        )
        == """
<!---{% set x = 5 %}-->
<!---{$ set y= fake::add(x, 5) $}--><!--{{y}}-->10<!--{><}-->
"""
    )


def inline_assignment_test():
    """Test that inline assignment works from a primitive."""
    assert (
        utils.inject("""<!--{% set df = 123 %}--><!--{{ df }}--><!--{><}-->""")
        == """<!--{% set df = 123 %}--><!--{{ df }}-->123<!--{><}-->"""
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
