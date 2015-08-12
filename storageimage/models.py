#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from wagtail.wagtailimages.models import AbstractImage, AbstractRendition  \
    get_upload_to, image_feature_detection, image_delete, rendition_delete \
    Image as wtImage, Rendition as wtRendition, get_image_model
from PIL import Image as PILImage

from storageimage import settings

class StorageImageFileDescriptor(models.fields.files.FileDescriptor):
    """
    Should this be a bugfix in Django? Original docstring and code below. When
    using a remote storage file, for some reason the forced
    update_dimension_fields on assignment were broken. Not sure if it's better
    not to force it, or have the forced thing behave better?

    Just like the FileDescriptor, but for ImageFields. The only difference is
    assigning the width/height to the width_field/height_field, if appropriate.
    
    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.name)
        super(ImageFileDescriptor, self).__set__(instance, value)

        # To prevent recalculating image dimensions when we are instantiating
        # an object from the database (bug #11084), only update dimensions if
        # the field had a value before this assignment.  Since the default
        # value for FileField subclasses is an instance of field.attr_class,
        # previous_file will only be None when we are called from
        # Model.__init__().  The ImageField.update_dimension_fields method
        # hooked up to the post_init signal handles the Model.__init__() cases.
        # Assignment happening outside of Model.__init__() will trigger the
        # update right here.
        if previous_file is not None:
            self.field.update_dimension_fields(instance, force=True)
    """

class StorageImageFieldFile(models.fields.files.ImageFieldFile):
    def _get_image_dimensions(self):
        # over-write so that it can actually read .width and .height of
        # a remote file
        pass

class StorageImageField(models.fields.files.ImageField):
    attr_class = StorageImageFieldFile

if settings.BY_INJECTION:
    from wagtail.wagtailimages.models import get_image_model
    ImageModel = get_image_model()
    RenditionModel = get_image_model().renditions.related.model
    ImageModel.file = StorageImageField(verbose_name=_('File'), upload_to=get_upload_to, width_field='width', height_field='height')
    RenditionModel.file = StorageImageField(upload_to='images', width_field='width', height_field='height')
else:
    class Image(AbstractImage):
        file = StorageImageField(verbose_name=_('File'), upload_to=get_upload_to, width_field='width', height_field='height')
        admin_form_fields = wtImage.admin_form_fields

    class Rendition(AbstractRendition):
        image = models.ForeignKey(Image, related_name='renditions')
        file = StorageImageField(upload_to='images', width_field='width', height_field='height')
        
        class Meta:
            unique_together = (
                ('image', 'filter', 'focal_point_key'),
            )

    pre_save.connect(image_feature_detection, sender=Image)
    pre_delete.connect(image_delete, sender=Image)
    pre_delete.connect(rendition_delete, sender=Rendition)
