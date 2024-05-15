class NoSuchDataScraperService(Exception):
    def __init__(self, message : str = "There isn't such a data scraper service implemented"):
        super().__init__(message)