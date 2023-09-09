from unittest import mock

from dynamic_markdown import utils

fake_adder = type("fake_module", (), {"add_and_shout": lambda x, y: x + y})


def set_and_get_test():
    """Test that we can get and set values."""
    assert (
        utils.inject(
            """<!--- $::set('x', 1243) --><!-- $::end --><!-- $::get('x') --><!-- $::end -->"""
        )
        == "<!--- $::set('x', 1243) --><!-- $::end --><!-- $::get('x') -->1243<!-- $::end -->"
    )


@mock.patch("sys.modules", new={"fake": fake_adder})
def use_global_test():
    import fake

    assert (
        (
            utils.inject(
                """
<!--- $::set("x", 5) --><!-- $::end -->
<!--- fake::add_and_shout($x, 5) --><!-- $::end -->
"""
            )
        )
        == """
<!--- $::set("x", 5) --><!-- $::end -->
<!--- fake::add_and_shout($x, 5) -->10<!-- $::end -->
"""
    )


def inline_assignment_test():
    """Test that inline assignment works from a primitive."""
    assert (
        utils.inject(
            """<!-- df = 123 --><!-- $::end --><!-- $::get("df") --><!-- $::end -->"""
        )
        == """<!-- df = 123 --><!-- $::end --><!-- $::get("df") -->123<!-- $::end -->"""
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
