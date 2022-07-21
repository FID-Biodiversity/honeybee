from unittest.mock import Mock

import pytest

from commons import create_url_from_parameters

spatial_fq_parameter_value = "{!bbox sfield=location}"
default_point_coordinates = "51.16336,10.44768"
default_distance_in_km = 50
default_number_of_hits_per_page = 100
default_cursor = "*"


class TestJsonViewResponse:
    @pytest.mark.parametrize(
        ["url_parameters", "expected_search_parameters"],
        [
            (  # Scenario - No query parameters given -> Use only default values
                {"format": "json"},
                {
                    "q": "*:*",
                    "fq": (spatial_fq_parameter_value,),
                    "pt": default_point_coordinates,
                    "d": default_distance_in_km,
                    "rows": default_number_of_hits_per_page,
                    "cursorMark": default_cursor,
                },
            ),
            (  # Scenario - Only starting year given
                {"format": "json", "yearStart": 1923},
                {
                    "q": "*:*",
                    "fq": tuple(["date:[1923-01-01 TO NOW]", spatial_fq_parameter_value]),
                    "pt": default_point_coordinates,
                    "d": default_distance_in_km,
                    "rows": default_number_of_hits_per_page,
                    'cursorMark': default_cursor
                },
            ),
            (  # Scenario - Multiple terms given
                {
                    "term": [
                        "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                        "https://www.biofid.de/ontologies/Tracheophyta/gbif/5678",
                    ],
                    "format": "json",
                },
                {
                    "q": 'taxa:("https\\://www.biofid.de/ontologies/Tracheophyta/gbif/1234" OR '
                    '"https\\://www.biofid.de/ontologies/Tracheophyta/gbif/5678")',
                    "fq": (spatial_fq_parameter_value,),
                    "pt": default_point_coordinates,
                    "d": default_distance_in_km,
                    "rows": default_number_of_hits_per_page,
                    'cursorMark': default_cursor
                },
            ),
            (  # Scenario - Point data given
                {
                    "term": "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                    "format": "json",
                    "radius": 10,
                    "lon": 50.1,
                    "lat": 8.6,
                },
                {
                    "q": 'taxa:("https\\://www.biofid.de/ontologies/Tracheophyta/gbif/1234")',
                    "fq": (spatial_fq_parameter_value,),
                    "pt": "8.6,50.1",
                    "d": 10,
                    "rows": default_number_of_hits_per_page,
                    'cursorMark': default_cursor
                },
            ),
            (  # Scenario - Resume Token given
                {
                    "term": "https://www.biofid.de/ontologies/Tracheophyta/gbif/1234",
                    "format": "json",
                    "resumeToken": "1234abcd",
                },
                {
                    "q": 'taxa:("https\\://www.biofid.de/ontologies/Tracheophyta/gbif/1234")',
                    "fq": (spatial_fq_parameter_value,),
                    "pt": default_point_coordinates,
                    "d": default_distance_in_km,
                    "cursorMark": "1234abcd",
                    "rows": default_number_of_hits_per_page,
                },
            ),
        ],
    )
    def test_return_map_json_data(
        self, client, url_parameters, expected_search_parameters, mock_solr_search
    ):
        base_url = "/map/search"
        url = create_url_from_parameters(base_url, url_parameters)

        response = client.get(url)

        assert response.status_code == 200
        mock_solr_search.assert_called_with(**expected_search_parameters)


@pytest.fixture
def mock_solr_search(monkeypatch, solr_response_with_geojson_field_only):
    from pysolr import Solr

    mock = Mock()
    mock.return_value = solr_response_with_geojson_field_only
    monkeypatch.setattr(Solr, name="search", value=mock)

    return mock
