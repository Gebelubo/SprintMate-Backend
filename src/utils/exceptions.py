class RepositoryError(Exception):
    pass


class EntityAlreadyExistsError(RepositoryError):
    pass


class ForeignKeyViolationError(RepositoryError):
    pass

class NotificationNotFoundError(Exception):
    pass


class NotificationAccessDeniedError(Exception):
    pass

class NotificationConfigNotFoundError(Exception):
    pass