# -*- coding: utf-8 -*-
"""Registro de modelos en la interfaz de admin de Django"""

__author__ = 'Sergio Ruiz Bens'

from django.db import models
from django.conf import settings
from django.contrib import admin
from django_jquery_ajax_combobox_admin.widgets import AjaxComboBoxWidget

__all__ = []

def field_form_ajax_combobox(self, db_field, *args,**kwargs):
    modelo_relacionado = db_field.related.parent_model
    app = db_field.related.parent_model._meta.app_label
    kwargs['widget'] = AjaxComboBoxWidget(model=modelo_relacionado, attrs={"field": "unicode","search_field": "admin_search_fields", "show_field": "unicode"})
    return db_field.formfield(**kwargs)

if settings.USE_ADMIN_COMBOBOX:
    for model in models.get_models():
        #A los modelos registrados en el admin le cambiamos el widget de los foreignkey
        if model in admin.site._registry:
            model.Admin = admin.site._registry[model]
            model.Admin.__class__.formfield_for_foreignkey = field_form_ajax_combobox
            admin.site._registry[model] = model.Admin.__class__(model, admin.site)
