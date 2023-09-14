from dynamic_markdown import processor


def if_test():
    assert (
        processor.process(
            """
<!--{% if 1 == 1%}-->
    <!--{{ "one egg is an oeuf" }}-->
<!--{%endif%}--><!--{><}-->"""
        )
        == """
<!--{% if 1 == 1%}-->
    <!--{{ "one egg is an oeuf" }}-->
<!--{%endif%}-->one egg is an oeuf<!--{><}-->"""
    )


def for_test():
    assert (
        processor.process(
            """<!--{%for i in range(5)%}--><!--{% if i%2  == 0%}--><!--{{ f'''{i} is even\n''' }}--><!--{% else%}--><!--{{ f'''{i} is odd\n''' }}--><!--{%endif%}--><!--{%endfor%}--><!--{><}-->"""
        )
        == """<!--{%for i in range(5)%}--><!--{% if i%2  == 0%}--><!--{{ f'''{i} is even
''' }}--><!--{% else%}--><!--{{ f'''{i} is odd
''' }}--><!--{%endif%}--><!--{%endfor%}-->0 is even
1 is odd
2 is even
3 is odd
4 is even
<!--{><}-->"""
    )


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main(["-v", "-s"] + sys.argv))
