
from argparse import Namespace, ArgumentParser

class CLIArguments:
    @staticmethod
    def parse() -> Namespace:
        parser : ArgumentParser = ArgumentParser(prog="web scraper", description="web scraper")
        parser.add_argument("--url", type=str, help="Url used to web scrape")
        return parser.parse_args()