#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models.fields.files import ImageFieldFile, ImageField 
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, pre_delete
from PIL import Image as PILImage
from storageimage import settings

class StorageImageFieldFile(ImageFieldFile):
    def _get_image_dimensions(self):
        # needs to be re-written to actually cache me.
        if not hasattr(self, '_dimensions_cache'):
            close = self.file.closed
            if close:
                self.file.open()
            else:
                file_pos = self.file.tell()
            self.file.read() # load the data from remote source

            img_pil = PILImage.open(self.file.file)
            self._dimensions_cache = img_pil.size

            if close:
                self.file.close()
            else:
                self.file.seek(file_pos)
        return self._dimensions_cache

class StorageImageField(ImageField):
    attr_class = StorageImageFieldFile

def storage_save(self,*args,**kwargs):
    fix_save = True
    if self.pk:
        instance_ref = self.__class__.objects.get(pk=self.pk)
        if instance_ref.file == self.file: 
            # This is a bad way of checking if the file changed...
            fix_save = False
    if fix_save:
        avail_name = get_upload_to(self, self.file.name)
        reopen = not self.file.file.closed
        if reopen:
            file_loc = self.file.file.tell()
        stored = self.file.storage.save(name=avail_name, content=self.file.file)
        self.file = self.file.storage.open(stored)
        if reopen:
            self.file.file.open()
            self.file.file.seek(file_loc)
    super(self.__class__, self).save(*args,**kwargs)


if settings.AUTO_INJECTION:
    from wagtail.wagtailimages.models import get_image_model, get_upload_to

    ImageModel = get_image_model()
    for i,f in enumerate(ImageModel._meta.local_fields):
        if f.name == 'file':
            del ImageModel._meta.local_fields[i]
            break
    StorageImageField(verbose_name=_('File'), upload_to=get_upload_to, width_field='width', height_field='height').contribute_to_class(ImageModel, 'file')
    ImageModel.save = storage_save

    RenditionModel = get_image_model().renditions.related.model
    for i,f in enumerate(RenditionModel._meta.local_fields):
        if f.name == 'file':
            del RenditionModel._meta.local_fields[i]
            break
    StorageImageField(verbose_name=_('File'), upload_to=get_upload_to, width_field='width', height_field='height').contribute_to_class(RenditionModel, 'file')
    RenditionModel.save = storage_save
