import argparse
import logging
import sys

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser


def process(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    parser = Parser(Language(tspython.language()))
    tree = parser.parse(data)

    assignments: dict[bytes, bytes] = {}
    interpolated_identifiers: set[bytes] = set()
    still_used_identifiers: set[bytes] = set()
    dos_newline = b"\r\n" in data
    newline_size = 2 if dos_newline else 1

    def traverse_tree(node: Node):
        yield node
        for n in reversed(node.children):
            yield from traverse_tree(n)

    # Find all assignment statements
    for node in traverse_tree(tree.root_node):
        match node:
            case Node(
                type="assignment",
                children=[
                    Node(type="identifier", text=lhs),
                    Node(type="="),
                    Node(
                        type="string",
                        children=[_, Node(type="string_content", text=rhs), _],
                    )
                    | Node(type="integer", text=rhs),
                ],
            ):
                assert lhs
                assert rhs
                assignments[lhs] = rhs

    # Find all interpolation expressions
    for node in traverse_tree(tree.root_node):
        match node:
            case Node(
                type="interpolation",
                children=[
                    Node(type="{"),
                    Node(type="identifier", text=identifier),
                    Node(type="}"),
                ],
            ):
                assert identifier
                if (val := assignments.get(identifier)) is not None:
                    interpolated_identifiers.add(identifier)
                    data = data[: node.start_byte] + val + data[node.end_byte :]

    tree = parser.parse(data)  # Re-parse the tree after edits

    # Find identifiers used in f-strings
    for node in traverse_tree(tree.root_node):
        match node:
            case Node(
                type="identifier",
            ) if node.parent is not None and node.parent.type != "assignment" and node.text in interpolated_identifiers:
                still_used_identifiers.add(node.text)

    # Remove no longer used identifiers
    unused_identifiers = interpolated_identifiers - still_used_identifiers
    for node in traverse_tree(tree.root_node):
        match node:
            case Node(
                type="assignment", children=[Node(type="identifier") as identifier, *_]
            ) if identifier.text in unused_identifiers:
                data = data[: node.start_byte] + data[node.end_byte + newline_size :]

    if args.inplace:
        with open(filepath, "wb") as f:
            data = f.write(data)
    else:
        sys.stdout.write(data.decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replaces string interpolation occurances with literal values of used identifiers."
    )
    parser.add_argument("file", type=str, nargs="+", help="Path to file")
    parser.add_argument(
        "--inplace", action="store_true", help="Whether to edit the file in place"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    for filepath in args.file:
        logging.info(f"Processing {filepath}")
        try:
            process(filepath)
        except FileNotFoundError:
            logging.error(f"File {filepath} not found")
