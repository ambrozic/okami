# Server

Okami server is a service to process in real time pages on a website implemented by spider.  

Override [HTTP_SERVER](settings.md#http_server) class when you wish to define custom server functionality.

## Start

- `okami server`

Access Okami server at [localhost:5566](http://localhost:5566). 

Use [HTTP_SERVER_ADDRESS](settings.md#http_server_address) or command line arguments to define custom address and port.


## Endpoints

**/process/**

- method
    - GET

- parameters
    - **name** *spider name*
    - **url** *page url*

- example
    - `/process/?name=example.com&url=http://example.com/product/id/`
