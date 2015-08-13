A custom image that allows a remote storage backend to be used. I wrote this to use the ftp backend of django-storages-redux on Heroku.

Use django-storages(-redux) to install a remote backend. Typically installation notes for that particular backend are in the python file defining the backend.::

  # settings.py
  DEFAULT_FILE_STORAGE = 'storages.backends.<backend_name>.<storage_name>'
  MEDIA_URL = '<http://your.media.url/path/to/files/client_side/>''
  MEDIA_ROOT = '/path/to/files/server_side/'
  # extra settings for your storage backend

Place ``storageimage`` before ``wagtail.wagtailimages`` in your ``INSTALLED_APPS`` list to inject the necessary fields/save method. Or you may set ``STORAGEIMAGE_SETTINGS['AUTO_INJECTION'] = False`` and write a custom Image model in the form shown below. Don't forget to have ``WAGTAILIMAGES_IMAGE_MODEL`` point to your new model!::

  # models.py
  from wagtail.wagtailimages.models import AbstractImage, AbstractRendition, \
      get_upload_to, image_feature_detection, image_delete, rendition_delete, \
      Image as wtImage, Rendition as wtRendition
  from storageimage.models import StorageImageField, storage_save

  class Image(AbstractImage):
      file = StorageImageField(verbose_name=_('File'), upload_to=get_upload_to, width_field='width', height_field='height')
      admin_form_fields = wtImage.admin_form_fields + []

      def save(self,*args,**kwargs):
          return storage_save(self,*args,**kwargs)

  class Rendition(AbstractRendition):
      image = models.ForeignKey(Image, related_name='renditions')
      file = StorageImageField(upload_to='images', width_field='width', height_field='height')

      def save(self,*args,**kwargs):
          return storage_save(self,*args,**kwargs)
    
      class Meta:
          unique_together = (
            ('image', 'filter', 'focal_point_key'),
          )

  pre_save.connect(image_feature_detection, sender=Image)
  pre_delete.connect(image_delete, sender=Image)
  pre_delete.connect(rendition_delete, sender=Rendition)

It works, but it's SLOW. TODO: On save, automatically generate known/common Renditions
