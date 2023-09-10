"""Generate a readme with content derived from python."""
import ast
import importlib
import logging
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

logger = logging.getLogger()

BLOCK = re.compile(
    r"<!-{2,3}\{([\{%\$>])\s*([\s\S]*?)(?:\s*|(?::\s*)(\S*?))([\}%\$<])\}-{2,3}>",
    re.M,
)
SET = re.compile(r"^set\s+([A-z_][A-z0-9_]*)\s*=\s*(.*)$")
CALL = re.compile(
    r"(?:set\s+([A-z_][A-z0-9_]*)\s*=\s*)?((?:[A-z_][A-z0-9_.]*)|\$)::(.*?)\s*(?:\((.*?)\))",
    re.M,
)

VARIABLE = re.compile(r"(?:,|^)(\s*[A-z_][A-z0-9_.]*\s*(?:,|$))")
KWARG_NAMES = re.compile(r"(?:[\s,]|^)(([A-z_][A-z\d_]*)\s*=)", re.M)


def convert_parameters(
    parameter_list: str, state
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
    for i, val_match in enumerate(VARIABLE.split(value_list)):
        if i % 2 == 1:
            values.append(state.get(val_match.rstrip(",").strip()))
        elif val_match:
            values.extend(ast.literal_eval(f"({val_match.rstrip(',').strip() },)"))
    if kwarg_names:
        return tuple(values[: -len(kwarg_names) :]), {
            k: v for k, v in zip(kwarg_names, values[-len(kwarg_names) :])
        }
    return tuple(values), {}


def _state(values: Optional[Dict[str, Any]] = None):
    """Create a state."""
    if values is None:
        values = {}

    return type(
        "state",
        (),
        {"set": values.__setitem__, "get": values.__getitem__, "__last": None},
    )


def process_control(
    content: str,
    state,
):
    """Process a control block."""
    if content.startswith("set "):
        key, value = next(SET.finditer(content)).groups()
        value = ast.literal_eval(value)
        state.set(key, value)
    else:
        raise RuntimeError(
            f"Unsupported control '{content.split(' ', maxsplit=1)[0]}'."
        )


def process_function(
    content: str,
    state,
):
    """Process a function block."""
    assign, module_path, fn, parameters = next(CALL.finditer(content)).groups()
    module = importlib.import_module(module_path)
    args, kwargs = convert_parameters(parameters, state)
    result = getattr(module, fn)(*args, **kwargs)
    if assign:
        state.set(assign, result)
    return result


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
    state = _state({})
    replacements: List[Tuple[int, int, str]] = []
    to_flush = None
    append_flush = False
    last_block = None
    for block in BLOCK.finditer(contents):
        lflag, content, format_spec, rflag = block.groups()
        if lflag == ">":
            replacements.append((last_block.end(0), block.start(0), str(to_flush)))
            to_flush = None
            append_flush = False
        else:
            if append_flush:
                replacements.append(
                    (last_block.end(0), block.start(0), str(to_flush) + "<!--{><}-->")
                )
                append_flush = False
            if lflag == "{":
                to_flush = state.get(content)
                append_flush = True
            elif lflag == "%":
                to_flush = process_control(content, state)
            elif lflag == "$":
                to_flush = process_function(content, state)
        if format_spec:
            to_flush = format(to_flush, format_spec)
        last_block = block

    if append_flush:
        replacements.append(
            (last_block.end(0), last_block.end(0), str(to_flush) + "<!--{><}-->")
        )
    for start, end, replacement in replacements[::-1]:
        contents = contents[:start] + replacement + contents[end:]

    return contents
