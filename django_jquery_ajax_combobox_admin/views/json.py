# -*- coding: utf-8 -*-

__author__ = "Sergio Ruiz Bens"

def json_api(request, id = None):
    from django.db.models import get_model
    from django.db.models import Q
    from django.contrib import admin
    from django.http import HttpResponse

    import simplejson
    import operator

    user = request.user

    #Se hace esto porque algunas versiones de Jquery añaden [] al nombre de los parametros con listas
    data = request.GET.copy()
    for key in request.GET.keys():
        if key.endswith("[]"):
            data.setlist(key.replace("[]", ""), data.pop(key))

    app_name = data["db_table"].split(".")[0]
    model_name = data["db_table"].split(".")[1]

    model = get_model(app_name, model_name)
    objetos = model.objects.all()

    #default: field == unicode
    display_field = data.get("field") or "unicode"

    if "base_query" in data and data["base_query"] != "":
        and_list = []
        for query in data["base_query"].split(","):
            lvalue = query.split("=")[0]
            rvalue = query.split("=")[1]
            and_list.append(Q(**{str(lvalue): eval(rvalue)}))
        objetos = objetos.filter(reduce(operator.and_, and_list)).distinct()

    #Select init_value
    if "pkey_val" in data:
        obj = objetos.get(**{data["pkey_name"]: data["pkey_val"]})
        if display_field == "unicode":
            str_obj = unicode(obj)
        else:
            str_obj = obj.__getattribute__(display_field)
        result = {"id": obj.id, display_field: str_obj}
        json_data = simplejson.dumps(result)
        response = HttpResponse(json_data, mimetype='application/json' )
        return response

    #Do query
    if "q_word" in data and data["q_word"] != "":
        search_fields = data.getlist("search_field")
        if search_fields[0] == "admin_search_fields" or search_fields[0] == "unicode":
            #Obtener el ModelAdmin y buscar en el search_fields
            model_admin_class = admin.site._registry[model]
            search_fields = model_admin_class.search_fields or model._meta.ordering

        query_list = []
        query_string = " ".join(data.getlist("q_word"))
        for search_field in search_fields:
            for query in query_string:
                lvalue = search_field.strip() + "__icontains"
                rvalue = query_string
                query_list.append(Q(**{str(lvalue): rvalue}))

        if "and_or" in data and data["and_or"] == "OR":
            objetos = objetos.filter(reduce(operator.or_, query_list))
        else:
            objetos = objetos.filter(reduce(operator.and_, query_list))

    if "order_by" in data:
        #default ",ASC"
        sort_field_list = data["order_by"].split(",")[:-1]
        if sort_field_list[0] != '' and sort_field_list[0] != 'admin_search_fields' and sort_field_list[0] != 'unicode':
            if data["order_by"].split(",")[-1] == "DESC":
                for i, sort_field in enumerate(sort_field_list):
                    sort_field_list[i] = '-' + sort_field
            #Se invierte la lista para aplicar la ordenacion en el orden indicado
            sort_field_list.reverse()
            for sort_field in sort_field_list:
                objetos = objetos.order_by(sort_field)

    lista=[]
    if "page_num" in data:
        inicio = (int(data["page_num"]) - 1) * int(data["per_page"])
        fin = inicio + int(data["per_page"])

    for obj in objetos[inicio:fin]:
        t = {'id' : obj.id, 'unicode': unicode(obj)}

        if len(data.getlist("show_field")) > 0:# and data.getlist("show_field")[-1] != "unicode":
            if data.getlist("show_field")[-1] == "*":
                return_fields = [x.name for x in model._meta.fields]
            else:
                return_fields = data.getlist("show_field")
                #if data.getlist("show_field")[-1] != "unicode" and data.getlist("show_field")[-1] not in return_fields:
                if display_field != "unicode" and display_field not in return_fields:
                    return_fields.append(data["field"])

            for field_name in return_fields:
                if field_name != "unicode":
                    field = obj._meta.get_field(field_name)
                    if field.__class__.__name__ == "ForeignKey":
                        t[field.name] = obj.__getattribute__(field.name) and obj.__getattribute__(field.name).pk
                    else:
                        t[field.name] = obj.__getattribute__(field.name) and unicode(obj.__getattribute__(field.name))

        lista.append(t)

    result = {"result": lista,
               "cnt_whole": objetos.count()}
    json_data = simplejson.dumps(result)
    response = HttpResponse(json_data, mimetype='application/json' )
    return response
