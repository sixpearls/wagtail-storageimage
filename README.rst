A custom image that allows a remote storage backend to be used.

Use django-storages(-redux) to install a remote backend. Typically installation notes for that particular backend are in the python file defining the backend. Then use storageimage as your image model.::

  # settings.py
  DEFAULT_FILE_STORAGE = 'storages.backends.<backend_name>.<storage_name>'
  MEDIA_URL = '<http://your.media.url/path/to/files/client_side/>''
  MEDIA_ROOT = '/path/to/files/server_side/'
  # extra settings for your storage backend
  WAGTAILIMAGES_IMAGE_MODEL = 'storageimage.Image'

Then, instead of importing directly from ``wagtailimages.models.Image``, use 
