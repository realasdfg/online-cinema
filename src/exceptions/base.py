class AppError(Exception):
    status_code: int = 500
    detail: str = "Internal server error."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class EntityNotFoundError(AppError):
    status_code = 404

    def __init__(self, entity_name: str, id_: int) -> None:
        self.entity_name = entity_name
        self.id_ = id_
        super().__init__(f"{entity_name} with id={id_} not found.")
