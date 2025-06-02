class GenericResponse:

    def __init__(self, data: dict = None):
        self.data = data if data is not None else {}

    def to_dict(self):
        return {
            "data": self.data
        }