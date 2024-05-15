from typing import List
from argparse import Namespace

from utils.helpers.cli_arguments import CLIArguments
from utils.errors.no_such_parameter_error import NoSuchParameterError
from utils.constants.error_messages import (
    MESSAGES, NO_MESSAGE
)
from services.factories.data_scraper_factory_service import DataScraperFactoryService
from interfaces.data_scraper import DataScraper
from utils.constants.url_to_enum_mapper import URL_TO_ENUM_MAP
from utils.enums.url_type import UrlType

if __name__ == "__main__":
    arguments : Namespace = CLIArguments.parse()
    url : str = arguments.url
    if url is None:
        raise NoSuchParameterError(message=MESSAGES.get("no_parameter_passed", NO_MESSAGE))

    data_scraper : DataScraper = DataScraperFactoryService.create(
        url=URL_TO_ENUM_MAP.get(url, UrlType.URL_NOT_IMPLEMENTED)
    )

    scraped_data : List[str] = data_scraper \
      .parse_url() \
      .get_html() \
      .transform() \
      .save() \
      .collect()
    print(scraped_data)
