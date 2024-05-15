from typing import Dict
from utils.enums.url_type import UrlType

URL_TO_ENUM_MAP : Dict[str, UrlType] = {
    "http://www.phpbb.com/community/viewtopic.php?f=46&t=2159437" : UrlType.URL_1,
    "https://forum.vbulletin.com/forum/vbulletin-3-8/vbulletin-3-8-questions-problems-and-troubleshooting/414325-www-vs-non-www-url-causing-site-not-to-login" : UrlType.URL_2
}