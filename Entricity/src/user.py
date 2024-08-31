class User:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super(User, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, 'initialized') and self.initialized:
            return
        self.username: str
        self.userd_id: str
        ...

        self.initialized = True
