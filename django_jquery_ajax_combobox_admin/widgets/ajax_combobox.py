# -*- coding: utf-8 -*-

__author__ = "Sergio Ruiz Bens"

import os

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

__all__ = ['AjaxComboBoxWidget',]

DEFAULT_LANG = "en"
try:
    if os.environ["LANG"].split("_")[0] in ["de", "en", "es", "pt-br"]:
        DEFAULT_LANG = os.environ["LANG"].split("_")[0]
except Exception:
    pass

add_min = ".min"
if settings.DEBUG:
    add_min = ""

class AjaxComboBoxWidget(forms.TextInput):
    """Widget para combobox ajax paginado
    Recibe el modelo
    Url que devuelve los datos en formato json (por dejecto json/json_api
    Recibe una lista de atributos de inicialización del combo (Los booleanos se específican como True o False)
    Ejemplo: widget = AjaxComboBoxWidget(model=CentroPracticum, attrs={"width": 500, "field": "nombre", "search_field": "nombre"})"""

    choices = []
    model = None
    label = None
    help_text = None

    def __init__(self, model=None, url="%s/json/json_api"%(settings.AJAX_COMBOBOX_BASE_URL), attrs=None, choices=[]):
        super(AjaxComboBoxWidget, self).__init__(attrs)
        # choices can be any iterable
        self.choices = choices
        self.url = url
        if model and "db_table" not in self.attrs:
            app_label =  model.__module__.split('.')[-2]
            if app_label == 'models':
                app_label = model.__module__.split('.')[-3]
            self.attrs["db_table"] = "%s.%s" % (app_label.lower(), model.__name__)

    def render(self, name, value, attrs=None):
        if 'width' in self.attrs:
            width_combobox = str(self.attrs['width']).replace("px", "").strip()
        else:
            width_combobox = 400
        html_combobox = u'<input style="width: %spx" name="%s" id="id_%s" />' % (width_combobox, name, name)
        result = u'%s<script type="text/javascript">%s</script>' % (html_combobox, self.render_js(name, value))
        return mark_safe(result)

    def render_js(self, name, value=None):
        html_script=''

        default_attrs = {
            "lang": DEFAULT_LANG,
            "and_or": "OR",
            "field": "unicode",
            "instance": True,
            "per_page": 20,
            "navi_num": 5,
            "select_only": True,
            "button_img": '%s/media/img/combobox_button.png' % settings.AJAX_COMBOBOX_BASE_URL,
            "loading_img": '%s/media/img/ajax-loader.gif' % settings.AJAX_COMBOBOX_BASE_URL
        }

        #Actualizamos los atributos por defecto con los que se reciben
        default_attrs.update(self.attrs)

        #Creamos la lista de atributos del combo: por ahora se aceptan los siguientes atributos
        #Atributos de tipo cadena: se le añaden comillas dobles
        #Atributos de tipo entero o flotante: se quedan igual
        #Atributos de tipo booleano: se pasan a minúscula ya que javascript usa true y false
        attrs_list = u''
        for attr in default_attrs:
            if attr != "width":
                if default_attrs[attr].__class__.__name__ == 'str' or default_attrs[attr].__class__.__name__ == 'unicode':
                    attrs_list = attrs_list + attr + ': "' + default_attrs[attr] + '", '
                if default_attrs[attr].__class__.__name__ == 'int' or default_attrs[attr].__class__.__name__ == 'float':
                    attrs_list = attrs_list + attr + ': ' + str(default_attrs[attr]) + ', '
                if default_attrs[attr].__class__.__name__ == "dict":
                    attrs_list = attrs_list + attr + ': ' + str(default_attrs[attr]) + ', '
                if default_attrs[attr] == True:
                    attrs_list = attrs_list + attr + ': true, '
                if default_attrs[attr] == False:
                    attrs_list = attrs_list + attr + ': false, '

        html_script = """var %s_instance = $('#id_%s').ajaxComboBox(
            '%s',
            {
                %s
                init_record: %s
            }
        );""" % (name.replace("-","_"), name, self.url, attrs_list, value or "false")

        return mark_safe(html_script)

    class Media:
        css = {
            'all': (settings.CSS_JQUERY_URL, settings.AJAX_COMBOBOX_BASE_URL + '/media/css/jquery.ajax-combobox%s.css' % add_min, settings.AJAX_COMBOBOX_BASE_URL + '/media/css/jquery.ajax-combobox-blue%s.css' % add_min)
        }
        #Jquery required
        js = (settings.JS_JQUERY_URL, settings.AJAX_COMBOBOX_BASE_URL + '/media/js/jquery.ajax-combobox%s.js' % add_min)
