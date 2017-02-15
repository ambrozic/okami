class OkamiException(Exception):
    msg = ""

    def __init__(self, msg=None, extra=None):
        if msg is not None:
            self.msg = msg
        self.extra = extra
        super().__init__(self.msg)


class OkamiTerminationException(OkamiException):
    pass


class NoSuchSpiderException(OkamiException):
    pass


class SpiderException(OkamiException):
    pass


class MiddlewareException(OkamiException):
    pass


class HttpMiddlewareException(MiddlewareException):
    pass


class PipelineException(OkamiException):
    pass


class StartupPipelineException(PipelineException):
    pass


class StatsPipelineException(PipelineException):
    pass


class RequestsPipelineException(PipelineException):
    pass


class ResponsesPipelineException(PipelineException):
    pass


class ItemsPipelineException(PipelineException):
    pass


class TasksPipelineException(PipelineException):
    pass
