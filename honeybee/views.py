from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    renderer_classes,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from honeybee.search import search_spatial_data
from honeybee import conf
from http import HTTPStatus
from honeybee.commons import UserInputException


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def search_view(request: Request) -> Response:
    """Generates a response holding georeferenced document data."""

    status_code = HTTPStatus.OK
    try:
        spatial_data = search_spatial_data(request.GET)
        content = {
            'spatialData': spatial_data
        }
    except UserInputException as ex:
        content = convert_exception_to_response_content(ex)
        status_code = HTTPStatus.BAD_REQUEST

    return Response(data=content, status=status_code)


def convert_exception_to_response_content(exception: Exception) -> dict:
    """ Takes a given exception and converts its content to an exception message. """
    return {
        conf.ERROR_MESSAGE_CONTENT_PARAMETER_NAME: exception.args[0]
    }
