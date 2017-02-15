class Middleware:
    """
    Base :class:`Middleware <okami.middleware.Middleware>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    """

    def __init__(self, controller):
        self.controller = controller

    async def before(self, something):
        """
        Processes passed object. Exceptions should be caught otherwise entire middleware terminates.

        :param something: an object
        :returns: altered passed object
        """
        raise NotImplementedError

    async def after(self, something):
        """
        Processes passed object. Exceptions should be caught otherwise entire middleware terminates.

        :param something: an object
        :returns: altered passed object
        """
        raise NotImplementedError


class TestMiddleware(Middleware):
    async def before(self, request):
        return request

    async def after(self, response):
        return response
