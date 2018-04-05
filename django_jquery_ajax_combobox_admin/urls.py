# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^json/json_api$','django_jquery_ajax_combobox_admin.views.json.json_api'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.realpath(os.path.join(os.path.dirname(__file__), 'media')), 'show_indexes': True}),
)

