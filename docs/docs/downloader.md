# Downloader

Receives a [Request](api.md#request) object from a http middleware *before* cycle and creates an HTTP request to a page. HTTP response is processed into a [Response](api.md#response) object, passed into http middleware *after* cycle and further into a spider for processing page data.

Override [DOWNLOADER](settings.md#downloader) class when you wish to define custom downloader functionality.
