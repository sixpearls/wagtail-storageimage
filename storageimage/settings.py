#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings


DEFAULT_SETTINGS = {
    "BY_INJECTION": True
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'STORAGEIMAGE_SETTINGS', {}))

globals().update(USER_SETTINGS)
