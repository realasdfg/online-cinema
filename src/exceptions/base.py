class EntityNotFoundError(Exception):
    def __init__(self, entity_name: str, id_: int):
        self.entity_name = entity_name
        self.id_ = id_
        super().__init__(f"{entity_name} with id={id_} not found")
