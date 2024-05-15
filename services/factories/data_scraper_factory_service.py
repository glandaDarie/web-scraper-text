from typing import Union

from interfaces.data_scraper import DataScraper
from utils.helpers.file_io import FileIO
from utils.enums.url_type import UrlType
from utils.constants.paths import PATH_OUTPUT_FILE_1, PATH_OUTPUT_FILE_2
from utils.errors.no_such_data_scraper_service import NoSuchDataScraperService
from services.builders.data_scraper_builder_service_1 import DataScraperBuilderService1
from services.builders.data_scraper_builder_service_2 import DataScraperBuilderService2

class DataScraperFactoryService:
    @staticmethod
    def create(url : Union[UrlType, None]) -> DataScraper:
        data_scraper : Union[DataScraper, None] = None
        
        if url == UrlType.URL_NOT_IMPLEMENTED:
            raise NoSuchDataScraperService()
        
        if url == UrlType.URL_1:
            data_scraper = DataScraperBuilderService1(url=url.value, standard_io=FileIO(path=PATH_OUTPUT_FILE_1))
        elif url == UrlType.URL_2:
            data_scraper = DataScraperBuilderService2(url=url.value, standard_io=FileIO(path=PATH_OUTPUT_FILE_2))
        else:
            raise NoSuchDataScraperService()
        
        return data_scraper