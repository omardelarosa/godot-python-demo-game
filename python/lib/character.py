import uuid


class Character:

    NULL_ID = "-1"

    DEFAULT_PROPERTIES = {
        "id": NULL_ID,
        "position": (0, 0, 0),
        "last_position": (0, 0, 0),
        "name": "Unnamed Character",
        "hit_points": 1,
        "team_id": NULL_ID,
    }

    def __init__(self, properties={}):
        self.id = (
            properties["id"] if "id" in properties else str(uuid.uuid4())
        )  # generates a uuid
        self.position = (
            properties["position"]
            if "position" in properties
            else Character.DEFAULT_PROPERTIES["position"]
        )
        self.last_position = (
            properties["last_position"]
            if "last_position" in properties
            else Character.DEFAULT_PROPERTIES["last_position"]
        )
        self.name = (
            properties["name"]
            if "name" in properties
            else Character.DEFAULT_PROPERTIES["name"]
        )
        self.hit_points = (
            properties["hit_points"]
            if "hit_points" in properties
            else Character.DEFAULT_PROPERTIES["hit_points"]
        )
        self.team_id = (
            properties["team_id"]
            if "team_id" in properties
            else Character.DEFAULT_PROPERTIES["team_id"]
        )

    def __iter__(self):
        """
        For supporting dict() casting...
        """
        yield "id", self.id
        yield "position", self.position
        yield "name", self.name
        yield "hit_points", self.hit_points
        yield "team_id", self.team_id,
        yield "last_position", self.last_position

    def __str__(self) -> str:
        return str(dict(self))