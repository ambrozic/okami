class Pipeline:
    """
    Base Pipeline <okami.pipeline.Pipeline>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        self.controller = controller

    async def initialise(self):
        """
        Executed at the beginning of scraping process. Exceptions should be caught or entire pipeline terminates.
        """
        pass

    async def process(self, something):
        """
        Processes passed object. Exceptions should be caught otherwise entire pipeline terminates.

        :param something: Any
        :return: something: Any
        """
        raise NotImplementedError

    async def finalise(self):
        """
        Executed at the end of scraping process. Exceptions should be caught or entire pipeline terminates.
        """
        pass


class Cache(Pipeline):
    async def process(self, spider):
        return spider


class Cleaner(Pipeline):
    async def process(self, items):
        return items


class Images(Pipeline):
    async def process(self, items):
        for item in items:
            for image in item.images:
                pass
        return items


class Parser(Pipeline):
    async def process(self, items):
        return items


class Settings(Pipeline):
    async def process(self, spider):
        return spider


class Tasks(Pipeline):
    async def process(self, tasks):
        return tasks
