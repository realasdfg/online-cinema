class UserAlreadyExistsError(Exception):
    def __init__(self, email):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")


class DefaultGroupNotFoundError(Exception):
    def __init__(self):
        super().__init__("Default 'USER' group is not seeded in the database.")
