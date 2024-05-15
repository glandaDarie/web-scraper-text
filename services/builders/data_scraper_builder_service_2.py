from typing import List, Tuple, Dict, Any, Union, Match
import re
from requests import (
    get as GET,
    Response
)
from requests.exceptions import JSONDecodeError, RequestException

from interfaces.data_scraper import DataScraper
from interfaces.standard_io import StandardIO
from utils.constants.error_messages import (
    MESSAGES, 
    NO_MESSAGE
)
from utils.constants.regex_patterns.url_2 import (
    REGEX_PIDS_PATTERN,
    REGEX_INNER_CONTENT_CLASS,
    REGEX_REMOVE_SPECIAL_CHARACTERS,
    REGEX_REPLACE_IMAGE_TITLE,
    REGEX_REPLACE_QUOT,
    REGEX_REMOVE_POST_SIGNATURE_RESTORE,
    REGEX_BBCODE_POSTED_BY_CONTENT, 
    REGEX_MESSAGE_CONTENT,
    REGEX_BBCODE_CONTAINER,
    REGEX_REMOVE_SPAN_CONTENT,
    REGEX_REMOVE_CLOSING_DIVS,
    REGEX_REMOVE_BRS,
    REGEX_CODE,
    REGEX_REMOVE_A_TAG,
    REGEX_REMOVE_BBCODE
)
from utils.errors.writing_to_file_error import WritingToFileError
from models.post import Post

class DataScraperBuilderService2(DataScraper):
    def __init__(self, url : str, standard_io : StandardIO):
        self.__url : str = url
        self.__query_params : Dict[str, Any] = {}
        self.__error_msg : Union[str, None] = None
        self.__content : Union[str, None] = None
        self.__standard_io : StandardIO = standard_io 
    
    def parse_url(self) -> "DataScraper":
        return self
    
    def get_html(self, **get_request_additional_params : Dict[str, Any]) -> "DataScraper":
        try:
            response : Response = GET(url=self.__url, params=self.__query_params, **get_request_additional_params)
            response.raise_for_status()
            self.__content : str = response.content.decode("utf-8")

        except JSONDecodeError as json_decode_error:
            self.__error_msg = MESSAGES.get("decode_json_error", NO_MESSAGE)
            
            if self.__error_msg != NO_MESSAGE:
                self.__error_msg = self.__error_msg.format(json_decode_error)
            
            json_decode_error.add_note(self.__error_msg)
            raise
        
        except RequestException as request_error:
            self.__error_msg = MESSAGES.get("request_error", NO_MESSAGE)

            if self.__error_msg != NO_MESSAGE:
                self.__error_msg = self.__error_msg.format(request_error)

            request_error.add_note(self.__error_msg)
            raise

        return self

    def transform(self) -> "DataScraper": 
        content : str = self.__content
        li_item_posts : List[str] = re.findall(
            pattern=REGEX_PIDS_PATTERN, 
            string=content,
            flags=re.DOTALL
        )
        posts : List[Post] = []
        bbcode_postedby_message_multiple_replies : List[List[Tuple[str, str]]] = []
        codes : List[str] = []
        for li_item_post in li_item_posts:
            
            li_item_post_content : List[str] = re.findall(
                pattern=REGEX_INNER_CONTENT_CLASS,
                string=li_item_post[-1],
                flags=re.DOTALL
            )

            li_item_post_content : str = re.sub(
                pattern=REGEX_REMOVE_SPECIAL_CHARACTERS, 
                repl="", 
                string=li_item_post_content[-1], 
                flags=re.DOTALL
            )

            find_title_matcher : Union[Match[str], None] = re.search(
                pattern=REGEX_REPLACE_IMAGE_TITLE, 
                string=li_item_post_content, 
                flags=re.DOTALL,
            ) 

            if find_title_matcher:
                emoji : str = f"({find_title_matcher.group(1)})"
                li_item_post_content = re.sub(
                    pattern=REGEX_REPLACE_IMAGE_TITLE, 
                    repl=emoji, 
                    string=li_item_post_content, 
                    flags=re.DOTALL
                )
                
            replacement_quot : str = r'"www"'
            li_item_post_content = re.sub(
                pattern=REGEX_REPLACE_QUOT, 
                repl=replacement_quot, 
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = re.sub(
                pattern=REGEX_REMOVE_POST_SIGNATURE_RESTORE,
                repl="",
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = re.sub(
                pattern=REGEX_REMOVE_A_TAG,
                repl=r"\1",
                string=li_item_post_content
            )

            bbcode_postedby_list : List[str] = re.findall(
                pattern=REGEX_BBCODE_POSTED_BY_CONTENT,
                string=li_item_post_content,
                flags=re.DOTALL
            )

            message_list : List[str] = re.findall(
                pattern=REGEX_MESSAGE_CONTENT,
                string=li_item_post_content,
                flags=re.DOTALL
            )

            message_list = [
                re.sub(
                    pattern=REGEX_REMOVE_SPAN_CONTENT,
                    repl="\n\n",
                    string=message,
                    flags=re.DOTALL
                )
                for message in message_list
            ]

            message_list = [
                 re.sub(
                    pattern=REGEX_REMOVE_BRS,
                    repl="",
                    string=message,
                    flags=re.DOTALL
                )
                for message in message_list
            ]

            message_list = [
                 re.sub(
                    pattern=REGEX_REMOVE_BBCODE,
                    repl="",
                    string=message,
                    flags=re.DOTALL
                )
                for message in message_list
            ]

            bbcode_postedby_list = [
                bbcode_postedby_item.replace("<strong>", "") 
                for bbcode_postedby_item in bbcode_postedby_list
            ]

            bbcode_postedby_message_multiple_replies.append([bbcode_postedby_list, message_list])
            
            message_list = [
                re.findall(
                    pattern=REGEX_REMOVE_BRS,
                    string=message,
                    flags=re.DOTALL
                )
                for message in message_list
            ]

            bbcode_container : Union[Match[str], None] = re.search(
                pattern=REGEX_CODE,
                string=li_item_post_content,
                flags=re.DOTALL
            )

            code : str = ""
            if bbcode_container:
                code = bbcode_container.group(2)
                code = self.__transform_code(code=code)
                
            codes.append(code)

            li_item_post_content = re.sub(
                pattern=REGEX_BBCODE_CONTAINER,
                repl="",
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = re.sub(
                pattern=REGEX_REMOVE_SPAN_CONTENT,
                repl="\n\n",
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = re.sub(
                pattern=REGEX_REMOVE_CLOSING_DIVS,
                repl="",
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = re.sub(
                pattern=REGEX_REMOVE_BRS,
                repl="",
                string=li_item_post_content,
                flags=re.DOTALL
            )

            li_item_post_content = li_item_post_content.strip()

            posts.append(
                Post(
                    data=li_item_post_content, 
                    is_replied=bool(re.search(r"Originally posted by <strong>(\w+)</strong>", li_item_post_content))
                )
            )
            
        codes = [code.lstrip() for code in codes]
        self.__content = self.__transform_data_to_respective_format_for_file(posts=posts, replies=bbcode_postedby_message_multiple_replies, codes=codes)
        return self

    def save(self) -> "DataScraper":
        error_msg : str = self.__standard_io.write(content=self.__content)
        if error_msg:
            raise WritingToFileError(message=error_msg)
        return self

    def collect(self) -> str:
        return self.__content
    
    def __transform_code(self, code : str) -> str:
        code = code.replace("&#91;", "[")
        code = code.replace("&#93;", "]")
        code = re.sub(r"(On)(RewriteCond)", r"\1\n\2", code)
        code = re.sub(r"(RewriteCond.*?)(RewriteRule)", r"\1\n\2", code)
        return code

    def __transform_data_to_respective_format_for_file(self, **results : Dict[str, Any]) -> str:
        result : str = ""
        
        for index, (post, reply, code) in enumerate(zip(results["posts"], results["replies"], results["codes"])):
            result += f"{index+1}.["
            if len(reply[0]) > 0 and len(reply[1]) > 0:
                for org_posted, message, in zip(reply[0], reply[1]):
                    result += f"{org_posted}\n{message}"
                    result += f"\n\n{post.data}\n\n"
                if code:
                    result += f"\n\nCode: \n\n{code}"
                result += "]\n\n"
                
            else:
                result += post.data
                if reply:  
                    pass
                
                if code:
                    result += f"\n\nCode: \n\n{code}"
                result += "]\n\n"
        
        return result
