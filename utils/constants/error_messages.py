from typing import Dict

NO_MESSAGE : str = "No such error message"
MESSAGES : Dict[str, str] = {
    "no_parameter_passed" : "Error: No --url parameter is passed when calling.",
    "file_not_found" : "File not found error: {}",
    "reading_file_error" : "File cannot be read error: {}",
    "write_to_file_error" : "Write to file error: {}",
    "decode_json_error" : "Failed to decode JSON error: {}",
    "request_error" : "Request error: {}",

}