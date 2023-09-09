"""CLI entrypoint for dynamic markdown generator.

If no file is supplied, uses the Readme.MD from the current working directory.
"""
import argparse
import glob

from dynamic_markdown.utils import inject


def create_parser():
    """Create the parser so this can be run from CLI."""
    parser = argparse.ArgumentParser("Generate markdown")
    readmes = glob.glob("[Rr][Ee][Aa][Dd][Mm][Ee].[Mm][Dd]")
    parser.add_argument("file", default=readmes[0] if readmes else None, nargs="?")
    return parser


parser = create_parser()
args = parser.parse_args()


with open(args.file, "r") as fp:
    content = inject(fp.read())

with open(args.file, "w") as fp:
    fp.writelines(content)
