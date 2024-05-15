from typing import List, Dict, Tuple, Any, Union, Match, Optional
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
from utils.errors.writing_to_file_error import WritingToFileError
from utils.constants.regex_patterns.url_1 import (
    REGEX_QUERY_PARAMS_PATTERN,
    REGEX_PIDS_PATTERN,
    REGEX_POST_CONTENT_ID,
    REGEX_POST_CONTENT_TEXT,
    REGEX_MATCH_CONTENT_AFTER_BLOCKQUOTE,
    REGEX_REMOVE_CONTENT_FROM_IMAGE,
    REGEX_REPLACE_BR_WITH_EMPTY_CHARACTER,
    REGEX_REMOVE_FROM_BLOCKQUOTE_TAGS
)
from models.post import Post

class DataScraperBuilderService1(DataScraper):
    def __init__(self, url : str, standard_io : StandardIO):
        self.__url : str = url
        self.__query_params : Dict[str, Any] = {}
        self.__error_msg : Union[str, None] = None
        self.__content : Union[str, None] = None
        self.__posts : List[Post] = []
        self.__standard_io : StandardIO = standard_io 

    def parse_url(self) -> "DataScraper":
        self.__url, str_query_params = self.__url.split("?")
        self.__query_params = dict(re.findall(pattern=REGEX_QUERY_PARAMS_PATTERN, string=str_query_params))
        self.__query_params = {
            key: int(value) if value.isdigit() else value 
            for key, value in self.__query_params.items()
        }

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
        matches_post_pids : List[str] = self.__get_all_post_ids(regex_id_matcher=REGEX_PIDS_PATTERN)
        is_replied : bool = False
        posts : Union[List[Post], str] = []
        for match_post_pid in matches_post_pids:
            pid : str = match_post_pid[0][1:]
            
            matches_post_content_ids : List[str] = re.findall(
                pattern=REGEX_POST_CONTENT_ID.format(pid), 
                string=self.__content, 
                flags=re.DOTALL
            )
            for match_post_content_id in matches_post_content_ids:
                content_id_first_div : str = match_post_content_id[0]
                content_id_second_div : str = match_post_content_id[1]
                matches_posts_content_text : List[str] = re.findall(
                    pattern=REGEX_POST_CONTENT_TEXT, 
                    string=content_id_first_div, 
                    flags=re.DOTALL
                )
                matcher_content_after_blockquote : Union[Match[str], None] = re.search(
                    pattern=REGEX_MATCH_CONTENT_AFTER_BLOCKQUOTE, 
                    string=content_id_second_div, 
                    flags=re.DOTALL
                )
                
                post : str = matches_posts_content_text[0][-1]
                post : str = self.__remove_content_from_image(post=post)
                post : str = self.__remove_br_tags(post=post)

                if matcher_content_after_blockquote:
                    is_replied, message_reply = self.__extract_message_reply(matcher_content_after_blockquote)
                    author, previous_question_post = self.__remove_blockquote_tags(post)

                    if author and previous_question_post:
                        post : str = self.__transform_post_reply(author=author, previous_question_post=previous_question_post, message_reply=message_reply)
                        post : str = self.__remove_br_tags(post)

                posts.append(Post(data=post, is_replied=is_replied))
        
        _, posts = self.__capitalize_repliers_name(posts=posts)
        self.__posts : str = self.__transform_data_to_respective_format_for_file(posts=posts)
        return self

    def save(self) -> "DataScraper":
        error_msg : str = self.__standard_io.write(content=self.__posts)
        if error_msg:
            raise WritingToFileError(message=error_msg)
        return self

    def collect(self) -> str:
        return self.__posts

    def __capitalize_repliers_name(self, posts : List[Post]) -> bool:
        reply_found : bool = False
        
        for post in posts:
            if post.is_replied:
                post_lines : List[str] = post.data.split("\n")
                if post_lines:
                    replier_name : str = post_lines[-1].capitalize()
                    post.data = "\n".join(post_lines[:-1])
                    post.data = f"{post.data}{replier_name}"
                    reply_found = True
            
        return reply_found, posts

    def __transform_data_to_respective_format_for_file(self, posts : List[Post]) -> str:
        return "\n\n".join([
            f"{index+1}.[{post.data.strip()}]" 
            for index, post in enumerate(posts)
        ])

    def __get_all_post_ids(self, regex_id_matcher : str, id_length : int = 8) -> List[str]:
        regex_id_matcher = regex_id_matcher.format(id_length)
        return re.findall(pattern=regex_id_matcher, string=self.__content)

    def __remove_content_from_image(self, post: str) -> str:
        return re.sub(
            pattern=REGEX_REMOVE_CONTENT_FROM_IMAGE,
            repl="",
            string=post,
            count=1,
            flags=re.DOTALL
        )
    
    def __remove_br_tags(self, post: str) -> str:
        return re.sub(
            pattern=REGEX_REPLACE_BR_WITH_EMPTY_CHARACTER,
            repl="",
            string=post
        )

    def __extract_message_reply(self, matcher : Match[str]) -> Tuple[bool, str]:
        is_replied : bool = True
        message_reply : Union[str, Any] = matcher.group(1).strip()
        
        return is_replied, message_reply
    
    def __remove_blockquote_tags(self, post : str) -> Tuple[Optional[str], Optional[str]]:
        matcher_blockquote_tags_removed = re.search(
            pattern=REGEX_REMOVE_FROM_BLOCKQUOTE_TAGS,
            string=post,
            flags=re.DOTALL
        )
        if matcher_blockquote_tags_removed:
            return matcher_blockquote_tags_removed.group(1), matcher_blockquote_tags_removed.group(2)
        
        return None, None
    
    def __transform_post_reply(self, author : str, previous_question_post : str, message_reply : str) -> str:
        return f"{author}\n{previous_question_post}\n\n{message_reply}"

