import simplejson

from django.http import HttpResponse
from django.core import serializers

__all__ = ('response', 'view', 'permission_required', 'Bail')

def response(data={}, status=200, message='OK'):
    """
    Wraps the arguments in a dictionary and returns a HttpResponse object with
    the HTTP status set to ``status``. The body of the response is JSON data
    on the format::

        {
            "status": 400,
            "message": "OK",
            "data": {"ids": [1, 2, 3]}
        }

    The content of ``data`` is serialized using the DjangoJSONEncoder class.

    Example::

        import jason

        def my_view(request):
            return jason.response({'weight': 80}, 200, 'OK')
    """
    response_data = {
        'data': data,
        'status': status,
        'message': message,
    }
    content = simplejson.dumps(response_data, ensure_ascii=False,
                               cls=serializers.json.DjangoJSONEncoder)
    return HttpResponse(content, status=status, content_type='application/json')


def view(allowed_methods, exceptions={}):
    """
    Decorates a Django function based view and wraps it's return in the
    :py:func:`jason.response` function. The view should return a list or tuple which is
    unpacked using the ``*``-operator into :py:func:`jason.response`.

    The view can raise a :py:class:`jason.Bail` Exception.

    ``allowed_methods`` lists which HTTP methods are allowed,
    e.g. ['GET', 'POST'].

    ``exceptions`` is a dictionary where the keys are ``Exception`` classes and
    values are callables. It defines responses for raised Exceptions other than
    the :py:class:`jason.Bail` Exception. The callable should return a tuple or list
    that can unpacked into :py:func:`jason.response`.

    Example::

        import jason

        @jason.view(allowed_methods=['GET', 'POST'], exceptions={
            WebFault: lambda e: ({}, 400, e.message, )
        })
        def my_view(request):
            return {'numbers': get_numbers()},
    """
    def _(f):
        def __(request, *args, **kwargs):
            if request.method not in allowed_methods:
                return response({}, 405, 'Method Not Allowed')
            try:
                return response(*f(request, *args, **kwargs))
            except Bail as e:
                return response(e.data, e.status, e.message)
            except Exception as e:
                if e.__class__ in exceptions:
                    return response(*exceptions[e.__class__](e))
                else:
                    return response({}, 500, 'Internal Server Error')
        return __
    return _


def permission_required(perm):
    """
    A json pendant to permission_required. Will return a 401 response if
    the user is not allowed. The body of the response will be the following json
    data::

        {
            "status": 401,
            "message": "Unauthorized",
            "data": {}
        }

    Example::

        import jason

        @jason.permission_required("my_perm")
        def my_view(request):
            ...
    """
    def _(f):
        def __(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return f(request, *args, **kwargs)
            else:
                return response({}, 401, 'Unauthorized')
        return __
    return _


class Bail(Exception):
    """
    This exception can be raised inside a view decorated by :py:func:`jason.view`. The
    arguments are the same as to :py:func:`jason.response`. When raised the return
    of the view will be the output of the :py:func:`jason.response` function.

    Example::

        import jason

        @jason.view(allowed_methods=['GET'])
        def my_view(request):
            if not_to_my_liking():
                raise jason.Bail({}, 400, 'Do not like!')

            ...
    """
    def __init__(self, data={}, status=400, message='Bad Request'):
        self.data = data
        self.status = status
        self.message = message