

class MyAppException(Exception):
    """Generic MyApp exception"""
    rc = 1



class UncommitedWork(MyAppException):
    "Raised when override uncommited backups"
    rc = 2

class MissingConfig(MyAppException):
    "Raised when configuration is not found"
    rc = 3
