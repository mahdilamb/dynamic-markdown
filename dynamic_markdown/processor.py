"""Generate a readme with content derived from python."""
import logging
import re
from types import MappingProxyType
from typing import List, Literal, Mapping, Optional, Tuple, TypeAlias

logger = logging.getLogger()


Mode: TypeAlias = Literal["evaluate", "clean"]
BLOCK_PATTERN = re.compile(
    r"<!-{2,3}\{([\{%\$>])\s*([\s\S]*?)(?:\s*|(?::\s*)(\S*?))([\}%\$<])\}-{2,3}>", re.M
)
FUNCTION_PATTERN = re.compile(
    r"(?:([A-Za-z_][A-Za-z0-9_.]*)|\$)(:{1,2})(?:[\s\S]*?)\s*(?:\((?:[\s\S]*?)\))",
    re.M,
)
INDENT_PATTERN = re.compile("^(for|if)")
UNINDENT_PATTERN = re.compile("^(endfor|endif)|(elif|else)")
BlockType: TypeAlias = Literal["control", "output", "flush", "function"]
BlockMap: Mapping[tuple[str, str], BlockType] = MappingProxyType(
    {
        ("%", "%"): "control",
        ("{", "}"): "output",
        (">", "<"): "flush",
        ("$", "$"): "function",
    }
)
Block: TypeAlias = Tuple[BlockType, str, Optional[str]]


def extract_blocks(
    contents: str,
) -> Tuple[Tuple[Block, ...], Tuple[Tuple[int, int], ...]]:
    """Extract the blocks that need to be processed.

    Return them along with the positions from which replacements need to be inserted.
    """
    blocks: List[Block] = []
    replacements: List[Tuple[int, int]] = []
    last_block = None
    append_flush = False
    for block in BLOCK_PATTERN.finditer(contents):
        lflag, content, format_spec, rflag = block.groups()
        block_type = BlockMap[(lflag, rflag)]
        blocks.append((block_type, content, format_spec))
        if block_type == "flush":
            replacements.append((last_block.end(0), block.start(0)))
            append_flush = False
        else:
            if append_flush:
                replacements.append((last_block.end(0), block.start(0)))
                append_flush = False
            if block_type == "output":
                append_flush = True
        last_block = block
    if append_flush:
        replacements.append((last_block.end(0), last_block.end(0)))
    return tuple(blocks), tuple(replacements)


def create_script(blocks: Tuple[Block, ...], function_name: str = "main") -> str:
    """Create a script from the blocks."""
    level = 1
    spacing = "  "
    current_output_name = f"__current_output"
    output_name = f"__output"
    script = [
        f"def {function_name}():",
        f'{spacing*level}{current_output_name} = ""',
        f"{spacing*level}{output_name} = []",
    ]
    for type, block, format_spec in blocks:
        _format_spec = '""' if format_spec is None else f'"{format_spec}"'
        if type == "function":
            for function in tuple(FUNCTION_PATTERN.finditer(block))[::-1]:
                path, module_or_path = function.groups()
                if len(module_or_path) == 2:
                    raise RuntimeError("Currently only module imports are supported.")
                else:
                    script += [f"{level * spacing}import {path}"]
                block = block[: function.start(2)] + "." + block[function.end(2) :]
        elif type == "control":
            if INDENT_PATTERN.match(block):
                script += [f"{level * spacing}{block}:"]
                level += 1
                continue
            else:
                try:
                    _, evaluate = next(UNINDENT_PATTERN.finditer(block)).groups()
                    level -= 1
                    if evaluate:
                        script += [f"{level * spacing}{block}:"]
                        level += 1
                    continue
                except StopIteration:
                    ...
        if type == "output":
            script += [
                f"{level * spacing}__{current_output_name} = {block.encode('unicode_escape').decode()}",
                f"{level * spacing}{current_output_name} += format(__{current_output_name}, {_format_spec})",
            ]
        elif type in ("control", "function"):
            script += [
                f"{level * spacing}{block}",
            ]
        elif type == "flush":
            script += [
                f"{level * spacing}{output_name}.append({current_output_name})",
                f"{level * spacing}{current_output_name} = ''",
            ]
    return "\n".join(script + [f"{spacing*1}return {output_name}"])


def run_script(script: str, function_name: str = "main") -> Tuple[str, ...]:
    """Run the script and extract the results."""
    __globals = {}
    __locals = {}
    exec(script, __globals, __locals)  # nosec B102
    return __locals[function_name]()


def process(contents: str, mode: Mode = "evaluate"):
    """Process some Markdown content and update it by processing the blocks."""
    blocks, replacements = extract_blocks(contents)
    if mode in ("evaluate",):
        script = create_script(blocks)
        results = run_script(script)
    else:
        results = [""] * len(replacements)
    output = contents
    for (start, end), result in zip(replacements[::-1], results[::-1]):
        output = output[:start] + result + output[end:]
    return output
