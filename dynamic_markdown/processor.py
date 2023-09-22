"""Generate a readme with content derived from python."""
import logging
import re
import uuid
from types import MappingProxyType
from typing import List, Literal, Mapping, Sequence, Tuple, TypeAlias, Union
from unittest import mock

logger = logging.getLogger()


DEFAULT_BLOCKED_IMPORTS = (
    "builtins.open",
    "builtins.input",
    "os.remove",
    "shutil.rmtree",
)
BLOCK_PATTERN = re.compile(
    r"<!-{2,3}\{(\{>|[\{%\$>])\s*([\s\S]*?)(?:\s*)(<\}|[\}%\$<])\}-{2,3}>",
    re.M,
)
CAPTURE_BLOCK = re.compile(r"", re.M)
INDENT_PATTERN = re.compile("^(for|if)")
UNINDENT_PATTERN = re.compile("^(endfor|endif)|(elif|else)")
Mode: TypeAlias = Literal["evaluate", "clean", "finalize"]
_BaseBlocks: TypeAlias = Literal["control", "capture", "flush"]
BlockType: TypeAlias = Union[Tuple[_BaseBlocks], Tuple[_BaseBlocks, Literal["flush"]]]
BlockMap: Mapping[tuple[str, str], BlockType] = MappingProxyType(
    {
        ("%", "%"): ("control",),
        ("{", "}"): ("capture",),
        (">", "<"): ("flush",),
        ("{>", "<}"): ("capture", "flush"),
    }
)
Block: TypeAlias = Tuple[BlockType, str]


def extract_blocks(
    contents: str,
) -> Tuple[str, Tuple[Block, ...], Tuple[Tuple[int, int], ...]]:
    """Extract the blocks that need to be processed.

    Return them along with the positions from which replacements need to be inserted.
    """
    blocks: List[Block] = []
    replacements: List[Tuple[int, int]] = []
    last_block = None
    for block in BLOCK_PATTERN.finditer(contents):
        lflag, content, rflag = block.groups()

        block_type = BlockMap[(lflag, rflag)]
        blocks.append((block_type, content))
        if "flush" in block_type:
            replacements.append(
                (last_block.end(0) if last_block else block.start(0), block.start(0))
            )
        last_block = block

    return contents, tuple(blocks), tuple(replacements)


def create_script(blocks: Tuple[Block, ...], function_name: str = "main") -> str:
    """Create a script from the blocks."""
    level = 0
    spacing = "  "
    script = []
    for type, block in blocks:
        if type == ("control",):
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
            script += [
                f"{level * spacing}{block}",
            ]
        elif type == ("capture",):
            script += [
                f"{level * spacing}{function_name}.capture(format({block.encode('unicode_escape').decode()}))",
            ]
        elif type == ("flush",):
            script += [
                f"{level * spacing}{function_name}.flush()",
            ]
        elif type == ("capture", "flush"):
            script += [
                f"{level * spacing}{function_name}.capture(format({block.encode('unicode_escape').decode()}))",
                f"{level * spacing}{function_name}.flush()",
            ]
    return "\n".join(script)


def run_script(
    script: str,
    function_name: str = "main",
    blocked_imports: Sequence[str] = DEFAULT_BLOCKED_IMPORTS,
) -> Tuple[str, ...]:
    """Run the script and extract the results."""
    observer, results = create_observer(function_name)
    __globals = {function_name: observer}
    __locals = {}
    patched = exec
    for blocked_import in blocked_imports:
        patched = mock.patch(
            blocked_import, new=observer.blocked_import(blocked_import)
        )(patched)
    patched(script, __globals, __locals)  # nosec B102
    return tuple(results[:-1]) if len(results) else ()


def create_observer(function_name: str):
    """Create the omniscient observer for script execution."""
    results = []

    def capture(content):
        if not (results):
            results.append(content)
        else:
            results[-1] += content

    def flush():
        results.append("")

    def blocked_import(name):
        def throw(*_, **__):
            raise RuntimeError(f"Using blocked import '{name}'.")

        return throw

    return (
        type(
            function_name,
            (),
            dict(flush=flush, capture=capture, blocked_import=blocked_import),
        ),
        results,
    )


def process(
    contents: str, mode: Mode = "evaluate", blocked_imports: Sequence[str] = ()
):
    """Process some Markdown content and update it by processing the blocks."""
    contents, blocks, replacements = extract_blocks(contents)
    function_name = f"__{uuid.uuid4().hex}__"

    if mode in ("evaluate", "finalize"):
        script = create_script(blocks, function_name)
        results = run_script(script, function_name, blocked_imports=blocked_imports)
    else:
        results = [""] * len(replacements)
    output = contents
    for (start, end), result in zip(replacements[::-1], results[::-1]):
        output = output[:start] + result + output[end:]
    if mode == "finalize":
        output = BLOCK_PATTERN.sub("", output)
    return output
