"""Generate a readme with content derived from python."""
import logging
import re
from types import MappingProxyType
from typing import List, Literal, Mapping, Optional, Tuple, TypeAlias

logger = logging.getLogger()

BLOCK_PATTERN = re.compile(
    r"<!-{2,3}\{([\{%\$>])\s*([\s\S]*?)(?:\s*|(?::\s*)(\S*?))([\}%\$<])\}-{2,3}>", re.M
)
FUNCTION = re.compile(
    r"(?:([A-Za-z_][A-Za-z0-9_.]*)|\$)(:{1,2})(?:[\s\S]*?)\s*(?:\((?:[\s\S]*?)\))",
    re.M,
)
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
) -> Tuple[Tuple[Block, ...], Tuple[Tuple[int, int, bool], ...]]:
    """Extract the blocks that need to be processed.

    Return them along with the positions from which replacements need to be inserted.
    """
    blocks: List[Block] = []
    replacements: List[Tuple[int, int, bool]] = []
    last_block = None
    append_flush = False
    for block in BLOCK_PATTERN.finditer(contents):
        lflag, content, format_spec, rflag = block.groups()
        block_type = BlockMap[(lflag, rflag)]
        blocks.append((block_type, content, format_spec))
        if block_type == "flush":
            replacements.append((last_block.end(0), block.start(0), False))
            append_flush = False
        else:
            if append_flush:
                replacements.append((last_block.end(0), block.start(0), True))
                append_flush = False
            if block_type == "output":
                append_flush = True
        last_block = block
    if append_flush:
        replacements.append((last_block.end(0), last_block.end(0), True))
    return tuple(blocks), tuple(replacements)


def create_script(blocks: Tuple[Block, ...]) -> str:
    """Create a script from the blocks."""
    level = 1
    spacing = "  "
    script = [
        "def main():",
        f'{spacing*level}__format_spec = ""',
        f"{spacing*level}__current_output = None",
        f"{spacing*level}__output = []",
    ]
    for type, block, format_spec in blocks:
        _format_spec = '""' if format_spec is None else f'"{format_spec}"'

        if type == "function":
            for function in tuple(FUNCTION.finditer(block))[::-1]:
                path, module_or_path = function.groups()
                if len(module_or_path) == 2:
                    raise RuntimeError("Currently only module imports are supported.")
                else:
                    script += [f"{level * spacing}import {path}"]
                block = block[: function.start(2)] + "." + block[function.end(2) :]

        if type in ("output", "control", "function"):
            script += [
                f"{level * spacing}__format_spec = {_format_spec}",
                f"{level * spacing}__current_output = {block}",
                f"{level * spacing}__current_output = format(__current_output, __format_spec)",
            ]
        elif type == "flush":
            script += [f"{level * spacing}__output.append(__current_output)"]
    return "\n".join(script + [f"{spacing*1}return __output"])


def run_script(script: str) -> Tuple[str, ...]:
    """Run the script and extract the results."""
    __globals = {}
    __locals = {}
    exec(script, __globals, __locals)  # nosec B102
    return __locals["main"]()


def process(contents: str):
    """Process some Markdown content and update it by processing the blocks."""
    blocks, replacements = extract_blocks(contents)
    script = create_script(blocks)
    results = run_script(script)
    output = contents
    for (start, end, append_flush), result in zip(replacements[::-1], results):
        if append_flush:
            result += "<!--{><}-->"
        output = output[:start] + result + output[end:]

    return output
