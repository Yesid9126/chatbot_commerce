# rest_framework
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):

    handlers = {
        'ValidationError': _handle_validation_error,
        'TypeError': _handle_generic_error,
        'HTTP404': _handle_generic_error,
        'PermissionDenied': _handle_generic_error,
    }

    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def _handle_validation_error(exc, context, response):
    print(context)
    data = {
        'solution': exc.error_list,
        'error_values': exc.params,
        'params': context.get('request').query_params
    }
    return Response(data=data, status=HTTP_400_BAD_REQUEST)


def _handle_generic_error(exc, context, response):
    data = {
        'errors': exc.error_list,
        'params': exc.params
    }
    return Response(data=data, status=HTTP_400_BAD_REQUEST)
