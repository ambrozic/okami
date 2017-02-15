VERSION = (0, 1, 4)


class status:
    OK = 0
    FAILED = 1
    RETRIAL = 2
    HTTP_404 = 404
    HTTP_500 = 500
    HTTP_501 = 501


class method:
    ANY = "*"
    CONNECT = "CONNECT"
    HEAD = "HEAD"
    GET = "GET"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


HTTP_FAILED = {
    status.HTTP_404,
    status.HTTP_500,
    status.HTTP_501,
}
FAILED = {status.FAILED} | HTTP_FAILED
