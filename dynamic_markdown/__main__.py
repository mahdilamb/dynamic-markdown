"""CLI entrypoint for dynamic markdown generator.

If no file is supplied, uses the Readme.MD from the current working directory.
"""
import argparse
import glob

from dynamic_markdown import processor


def main():
    """Run the updater."""

    def create_parser():
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

        parser.add_argument("--in-file", default=default_in, nargs="?")
        parser.add_argument("--out-file", default=default_out, nargs="?")
        parser.add_argument(
            "--mode", default="evaluate", choices=processor.Mode.__args__
        )
        return parser

    parser = create_parser()
    args = parser.parse_args()
    if args.out_file is None:
        args.out_file = args.in_file

    with open(args.in_file, "r") as fp:
        content = processor.process(fp.read(), mode=args.mode)

    with open(args.out_file, "w") as fp:
        fp.writelines(content)


if __name__ == "__main__":
    main()
