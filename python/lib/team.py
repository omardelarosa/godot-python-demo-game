import uuid


class Team:

    NULL_ID = "-1"

    DEFAULT_PROPERTIES = {
        "id": NULL_ID,
        "name": "Unnamed Team",
    }

    def __init__(self, properties={}):
        self.id = (
            properties["id"] if "id" in properties else str(uuid.uuid4())
        )  # generates a uuid
        self.name = (
            properties["name"]
            if "name" in properties
            else Team.DEFAULT_PROPERTIES["name"]
        )

    def __iter__(self):
        """
        For supporting dict() casting...
        """
        yield "id", self.id
        yield "name", self.name

    def __str__(self) -> str:
        return str(dict(self))