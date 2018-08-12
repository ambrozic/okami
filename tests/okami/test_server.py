import json
from unittest import mock

import pytest

from okami.api import Result
from okami.exceptions import NoSuchSpiderException
from okami.server import Server
from tests.factory import Factory


def test_server___init__():
    server = Server(address="1.0.0.0:5566")
    assert server.name == "Okami API Server"
    assert server.address == "1.0.0.0:5566"
    assert ["index", "process"] == [r._name for r in server.app.router._resources]
    assert ["/", "/process/"] == [r._path for r in server.app.router._resources]
    assert server.controllers == dict()


def test_server_start(capsys):
    with mock.patch("okami.server.web") as web:
        web.run_app = mock.Mock()
        server = Server(address="1.0.0.0:5566")
        server.start()
        captured = capsys.readouterr()
        assert captured.out == "Okami API Server at http://1.0.0.0:5566\n"
        assert web.run_app.call_count == 1
        assert web.run_app.call_args == mock.call(app=server.app, host="1.0.0.0", port="5566", print=None)


@pytest.mark.asyncio
async def test_server_view_index():
    response = await Server(address="1.0.0.0:5566").view_index(request=mock.Mock())
    assert b"Okami API Server - Python/" in response.body
    assert response.body_length == 0
    assert response.content_length == 43
    assert response.headers == {"Content-Type": "text/plain; charset=utf-8"}
    assert response.status == 200
    assert response.content_type == "text/plain"
    assert response.reason == "OK"
    assert response.task is None


@pytest.mark.asyncio
async def test_server_view_process(factory: Factory, coro):
    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = [factory.obj.product.create(), factory.obj.product.create()]
    with mock.patch("okami.server.Controller") as controller:
        controller.return_value.process = mock.Mock(
            side_effect=coro(
                mock.Mock(side_effect=[Result(status="status", task="task", tasks=tasks, items=items)])
            )
        )
        query_string = "name=example.com&url=http://localhost:8000/men-backpacks/142000/"
        response = await Server(address="1.0.0.0:5566").view_process(request=mock.Mock(query_string=query_string))
        assert json.loads(response.body) == [{"iid": "IID", "name": "NAME"}, {"iid": "IID", "name": "NAME"}]
        assert response.body_length == 0
        assert response.content_length == 118
        assert response.headers == {"Content-Type": "application/json; charset=utf-8"}
        assert response.status == 200
        assert response.content_type == "application/json"
        assert response.reason == "OK"
        assert response.task is None

    query_string = "{\"name\":\"example.com\", \"url\":\"URL\"}"
    with pytest.raises(NoSuchSpiderException):
        await Server(address="1.0.0.0:5566").view_process(request=mock.Mock(query_string=query_string))
