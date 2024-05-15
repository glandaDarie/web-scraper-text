from typing import Dict, Any
from abc import ABC, abstractmethod

class DataScraper(ABC):
    @abstractmethod
    def parse_url(self) -> "DataScraper":
        pass
    
    @abstractmethod
    def get_html(self, **get_request_additional_params : Dict[str, Any]) -> "DataScraper":
        pass
    
    @abstractmethod
    def transform(self) -> "DataScraper":
        pass

    @abstractmethod
    def save(self) -> "DataScraper":
        pass

    @abstractmethod
    def collect(self) -> str:
        pass