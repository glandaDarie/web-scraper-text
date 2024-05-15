class Post:
    def __init__(self, data : str, is_replied : bool): 
        self.__is_replied : bool = is_replied
        self.__data : str = data
    
    @property
    def data(self) -> str:
        return self.__data
    
    @data.setter
    def data(self, new_post : str) -> None: 
        self.__data = new_post
    
    @property
    def is_replied(self) -> bool:
        return self.__is_replied

    @is_replied.setter
    def is_replied(self, new_is_replied : bool) -> None:
        self.__is_replied = new_is_replied

    def __str__(self) -> str:
        return f"Post(data={self.__data}, is_replied={self.__is_replied})"