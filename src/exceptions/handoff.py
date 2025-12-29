class HandoffError(Exception):
    pass

class InvalidStateTransition(HandoffError):
    pass

class UnauthorizedActor(HandoffError):
    pass

class HandoffNotFound(HandoffError):
    pass