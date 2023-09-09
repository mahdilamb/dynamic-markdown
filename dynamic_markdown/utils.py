"""Generate a readme with content derived from python."""
import ast
import importlib
import logging
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

logger = logging.getLogger()
MODULE = re.compile(r"((?:[A-z_][A-z0-9_.]*)|\$)::(.*?)\s*(?:\((.*?)\))", re.M)
BLOCK = re.compile(
    r"<!-{2,3}\s*(?:(?:"
    + MODULE.pattern
    + r"(?::(\S*))?)|(?:([A-z_][A-z0-9_]*)\s*=\s*([\s\S]*?)))\s*-{2,3}>([\S\s]*?)<!-{2,3}\s*\$::end\s*-{2,3}>",
    re.M,
)
GLOBAL_VARIABLE = re.compile(r"(\$[A-z_][A-z0-9_.]*\s*,?)")
KWARG_NAMES = re.compile(r"(?:[\s,]|^)(([A-z_][A-z\d_]*)\s*=)", re.M)


def convert_parameters(
    parameter_list: str, env
) -> Tuple[Iterable[Any], Mapping[str, Any]]:
    """Convert a parameter list to args and kwargs.

    Parameters
    ----------
    parameter_list : str
        A string containing the parameter list.

    Returns
    -------
    Tuple[Iterable[Any], Mapping[str, Any], Mapping[int,str]]
        The args and kwargs from the parameter list. And, additionally the positions to insert the globals into.
    """
    kwarg_name_matches = tuple(KWARG_NAMES.finditer(parameter_list))
    kwarg_names = tuple(k.group(2) for k in kwarg_name_matches)
    value_list = parameter_list
    for kwarg in kwarg_name_matches[::-1]:
        value_list = value_list[: kwarg.start(1)] + value_list[kwarg.end(0) :]
    values = []
    for i, val_match in enumerate(GLOBAL_VARIABLE.split(value_list)):
        if i % 2 == 1:
            values.append(env.get(val_match.strip()[1]))
        elif val_match:
            values.extend(ast.literal_eval(f"({val_match.strip(',') },)"))
    if kwarg_names:
        return tuple(values[: -len(kwarg_names) :]), {
            k: v for k, v in zip(kwarg_names, values[-len(kwarg_names) :])
        }
    return tuple(values), {}


def _environment(values: Optional[Dict[str, Any]] = None):
    """Create an environment."""
    if values is None:
        values = {}

    return type(
        "environment", (), {"set": values.__setitem__, "get": values.__getitem__}
    )


def inject(contents: str) -> str:
    """Substitute the values in a markdown file using the evaluated results.

    Parameters
    ----------
    contents : str
        The contents of the markdown file.

    Returns
    -------
    str
        The new contents of the markdown file.
    """
    env = _environment({})
    replacements: List[Tuple[int, int, str]] = []

    for to_replace in BLOCK.finditer(contents):
        (
            module_path,
            fn,
            parameters,
            format_spec,
            assignment,
            assignee,
            _,
        ) = to_replace.groups()

        if assignee:
            try:
                env.set(assignment, ast.literal_eval(assignee))
            except SyntaxError as e:
                try:
                    module_path, fn, parameters = next(
                        MODULE.finditer(assignee)
                    ).groups()
                    assignee = None
                except StopIteration as ee:
                    raise ee from e
        if not assignee:
            if module_path == "$":
                module = env
            elif module_path:
                module = importlib.import_module(module_path)
            args, kwargs = convert_parameters(parameters, env)
            result = getattr(module, fn)(*args, **kwargs)
            if assignment:
                env.set(assignment, result)
                result = None
            if result is None:
                continue
            if format_spec:
                result = format(result, format_spec)
            else:
                result = str(result)
            replacements.append((to_replace.start(7), to_replace.end(7), result))
    for start, end, replacement in replacements[::-1]:
        contents = contents[:start] + replacement + contents[end:]

    return contents
