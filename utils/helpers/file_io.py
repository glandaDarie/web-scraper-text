from typing import Union, Tuple
from utils.constants.error_messages import (
    MESSAGES, 
    NO_MESSAGE
)
from interfaces.standard_io import StandardIO

class FileIO(StandardIO):
    def __init__(self, path : str):
        self.__path : str = path
    
    def read(self) -> Tuple[Union[str, None], Union[str, None]]:
        error_msg : Union[str, None] = None
        out_data : Union[str, None] = None
        
        try:
            with open(file=self.__path, mode="r") as input_file:
                out_data = input_file.read()
                return error_msg, out_data
            
        except FileNotFoundError as file_not_found_error:
            error_msg = MESSAGES.get("file_not_found", NO_MESSAGE)
            if error_msg != NO_MESSAGE:
                error_msg = error_msg.format(file_not_found_error)

        except Exception as error:
            error_msg = MESSAGES.get("cant_read_file", NO_MESSAGE)
            if error_msg != NO_MESSAGE:
                error_msg = error_msg.format(error)

        return error_msg, out_data
    
    def write(self, content : str) -> Union[str, None]:
        error_msg : Union[str, None] = None
        try:
            with open(file=self.__path, mode="w") as output_file:
                output_file.write(content)
        except Exception as error:
            error_msg = MESSAGES.get("write_to_file_error", NO_MESSAGE)
            if error_msg != NO_MESSAGE:
                error_msg = error_msg.format(error)

        return error_msg