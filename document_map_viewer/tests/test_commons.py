from typing import Iterable

import pytest
from django.http import QueryDict

from document_map_viewer.commons import get_from_data
from document_map_viewer.tests.commons import create_url_from_parameters

GET_STRING = "GET"
POST_STRING = "POST"


class TestDataExtractionFromRequest:
    @pytest.mark.parametrize(
        ["request_data", "function_parameters", "expected_values"],
        [
            # Scenario - Required parameter
            (
                {"format": "json"},
                ({"name": "format", "parameter_type": str, "optional": False},),
                ("json",),
            ),
            # Scenario - Optional parameter not given, but type checked
            (
                    {},
                    ({"name": "radius", "parameter_type": int, "optional": True, 'default': None},),
                    (None,),
            ),
            # Scenario - Required and optional parameters, both given
            (
                {
                    "term": "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                    "format": "json",
                },
                (
                    {"name": "format", "parameter_type": str, "optional": False},
                    {"name": "term", "parameter_type": str, "optional": True},
                ),
                ("json", "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234"),
            ),
            # Scenario - Required and optional parameters, only required given
            (
                {
                    "format": "json",
                },
                (
                    {"name": "format", "parameter_type": str, "optional": False},
                    {
                        "name": "term",
                        "parameter_type": str,
                        "optional": True,
                        "default": "*:*",
                    },
                ),
                ("json", "*:*"),
            ),
            # Scenario - Mixed parameter types
            (
                {
                    "term": "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                    "format": "json",
                    "radius": 10,
                    "lon": 50.1,
                    "lat": 8.6,
                },
                (
                    {"name": "format", "parameter_type": str, "optional": False},
                    {
                        "name": "term",
                        "parameter_type": str,
                        "optional": True,
                        "default": "*:*",
                    },
                    {"name": "radius", "parameter_type": int, "optional": True},
                    {"name": "lon", "parameter_type": float, "optional": True},
                    {"name": "lat", "parameter_type": float, "optional": True},
                ),
                (
                    "json",
                    "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                    10,
                    50.1,
                    8.6,
                ),
            ),
            # Scenario - Parameter is list
            (
                {"numbers": [1, 2, 3]},
                (
                    {
                        "name": "numbers",
                        "parameter_type": float,
                        "is_list": True,
                        "optional": False,
                    },
                ),
                ([1.0, 2.0, 3.0],),
            ),
        ],
        indirect=["request_data"],
    )
    def test_get_from_data_for_valid_data(
        self, request_data: QueryDict, function_parameters, expected_values
    ):
        self.assert_value_extraction_with_get_from_data(
            request_data, function_parameters, expected_values
        )

    @pytest.mark.parametrize(
        ["request_data", "function_parameters", "expected_exception"],
        [
            (  # Scenario - Mandatory parameter "term" is missing
                {"radius": "test"},
                ({"name": "term", "parameter_type": str, "optional": False},),
                LookupError,
            ),
            (  # Scenario - Given parameter value is not of the expected type
                {"radius": "test"},
                ({"name": "radius", "parameter_type": int, "optional": False},),
                ValueError,
            ),
        ],
        indirect=["request_data"],
    )
    def test_get_from_data_for_invalid_data(
        self, request_data: QueryDict, function_parameters, expected_exception
    ):
        irrelevant_dummy_list = [None]

        with pytest.raises(expected_exception):
            self.assert_value_extraction_with_get_from_data(
                request_data, function_parameters, irrelevant_dummy_list
            )

    def assert_value_extraction_with_get_from_data(
        self, request_data, function_parameters: Iterable, expected_values
    ):
        for parameters, value in zip(function_parameters, expected_values):
            assert get_from_data(request_data, **parameters) == value


@pytest.fixture
def request_data(request, rf, request_type: str):
    base_url = "/test"
    url_parameters = request.param

    url = create_url_from_parameters(base_url, url_parameters)

    if request_type == GET_STRING:
        request = rf.get(url)
    elif request_type == POST_STRING:
        request = rf.post(url)
    else:
        raise ValueError()

    return request.GET


@pytest.fixture(params=[GET_STRING, POST_STRING])
def request_type(request):
    return request.param
