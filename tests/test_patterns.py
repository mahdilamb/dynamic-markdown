from dynamic_markdown import utils

ENV = utils._environment()


def parameter_list_test():
    """Test that a variety of parameter list get correctly parsed."""
    assert utils.convert_parameters('1,2,h="j", sdf=123', ENV) == (
        (1, 2),
        {"h": "j", "sdf": 123},
    )
    assert utils.convert_parameters("1,2", ENV) == ((1, 2), {})
    assert utils.convert_parameters("1", ENV) == ((1,), {})
    assert utils.convert_parameters("", ENV) == ((), {})
    assert utils.convert_parameters('h="j"', ENV) == ((), {"h": "j"})
    assert (
        utils.convert_parameters(
            '''h="""I wanna go home, 


(123123)"""''',
            ENV,
        )
        == (
            (),
            {
                "h": """I wanna go home, 


(123123)"""
            },
        )
    )
    assert (
        utils.convert_parameters(
            '''"""I wanna go home, 


(123123)"""''',
            ENV,
        )
        == (
            (
                """I wanna go home, 


(123123)""",
            ),
            {},
        )
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
