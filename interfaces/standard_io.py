from typing import Union, Tuple
from abc import ABC, abstractmethod

class StandardIO(ABC):
    @abstractmethod
    def read(self) -> Tuple[Union[str, None], Union[str, None]]:
        pass
    
    @abstractmethod
    def write(self, content : str) -> Union[str, None]:
        pass 