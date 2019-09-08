""" Eda.ru parser application. """

import argparse

from eda_ru_parser.parser import main as parser_main


def run() -> None:
    """ CLI for the app. """
    parser = argparse.ArgumentParser(prog="eda_ru_parser", description="Parser for eda.ru site")
    parser.add_argument("--output", type=str, help="name of the output folder", required=True)

    args = parser.parse_args()

    parser_main(args)


if __name__ == "__main__":
    run()
