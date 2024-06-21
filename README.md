# data-replay camera modular service

*data-replay* is a Viam modular service that provides camera capabilities, returning images from a [Viam dataset](https://docs.viam.com/tutorials/services/data-mlmodel-tutorial/#tag-images-and-create-a-dataset) based on a dataset ID.

The model this module makes available is *mcvella:camera:data-replay*

## Prerequisites

You must have created a dataset using [Viam Data Management](https://docs.viam.com/tutorials/services/data-mlmodel-tutorial/#the-data-management-service)

## API

The data-replay resource implements the [RDK camera API](https://github.com/rdk/camera-api), specifically get_image().

### get_image

On each get_image() call, the next image from the dataset (default search order) will be returned.
After the last image is returned, the next get_image() call will return the first image from the dataset.
Note that currently, the module must be reconfigured or restarted in order for the images in the dataset to be re-loaded.

The following can be passed via the *get_image()* extra parameter:

#### dataset_id (string)

The dataset_id to return images from.
This overrides the default_dataset_id.

Example:

```python
camera.get_image() # returns the next image from the dataset specified via config default_dataset_id
camera.get_image(extra={"dataset_id":"mydatasetid123"}) # returns the next image from the dataset id "mydatasetid123"
```

## Viam Service Configuration

Example attribute configuration:

```json
{
    "default_dataset_id": "mydatasetid123",
    "app_api_key_id": "xyz123",
    "app_api_key": "keyid"
}
```

### Attributes

The following attributes are available for `mcvella:camera:data-replay` model:

| Name | Type | Inclusion | Description |
| ---- | ---- | --------- | ----------- |
| `default_dataset_id` | string | **Required** |  Default dataset ID. Can be overridden via extra params on get_image() calls. |
| `app_api_key_id` | string | **Required** |  Viam app key id. Required in order to read from Viam datasets. |
| `app_api_key` | string | **Required** |  Viam app key. Required in order to read from Viam datasets. |
