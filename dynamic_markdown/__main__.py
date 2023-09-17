"""CLI entrypoint for dynamic markdown generator.

If no file is supplied, uses the Readme.MD from the current working directory.
"""
import argparse
import glob

from dynamic_markdown import processor


def main():
    """Run the updater."""

    def get_args():
        """Create the parser so this can be run from CLI."""
        parser = argparse.ArgumentParser("Generate markdown")
        readmes = glob.glob("[Rr][Ee][Aa][Dd][Mm][Ee].[Mm][Dd]*")
        default_in = default_out = None
        if len(readmes) == 1:
            default_in = default_out = readmes[0]
        elif len(readmes):
            for readme in readmes:
                if readme.lower().endswith(".in"):
                    default_in = readme
                elif readme.lower().endswith(".md"):
                    default_out = readme

        parser.add_argument("--file", default=default_in, nargs="?")
        parser.add_argument("--output", nargs="?")
        parser.add_argument(
            "mode", default="evaluate", choices=processor.Mode.__args__, nargs="?"
        )
        parser.add_argument("--blocked-imports", nargs="+")
        parser.add_argument("--additional-blocked-imports", nargs="+")
        args = parser.parse_args()
        if args.blocked_imports is None:
            args.blocked_imports = processor.DEFAULT_BLOCKED_IMPORTS
        else:
            args.blocked_imports = tuple(imp for imp in args.blocked_imports if imp)
        if args.additional_blocked_imports is not None:
            args.blocked_imports = args.blocked_imports + tuple(
                imp for imp in args.additional_blocked_imports if imp
            )
        delattr(args, "additional_blocked_imports")

        if args.output is None:
            if args.file is not default_in:
                args.output = args.file
            else:
                args.output = default_out
        return args

    args = get_args()
    if args.output is None:
        args.output = args.file

    with open(args.file, "r") as fp:
        content = processor.process(
            fp.read(), mode=args.mode, blocked_imports=args.blocked_imports
        )

    with open(args.output, "w") as fp:
        fp.writelines(content)


if __name__ == "__main__":
    main()
