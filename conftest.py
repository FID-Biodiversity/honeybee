import json

import pysolr
import pytest

pytest_plugins = ["honeybee.tests.parameters"]


@pytest.fixture
def single_point_geojson_in_feature_collection():
    """A GeoJson Feature collection containing only a single point with its source properties."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "https://www.biofid.de/document/12345/d073lo8ewf",
                "geometry": {"type": "Point", "coordinates": [50.11552, 8.68417]},
                "properties": {
                    "time": "1836-01-01",
                    "taxa": [
                        "https://www.biofid.de/ontologies/Vogel",
                        "https://www.biofid.de/ontologies/Fagus",
                    ],
                    "source": "https://www.ub.uni-frankfurt/12345",
                    "parent-label": "Some article title",
                    "sentence": '<sentence id="9364">Ich fand einen <em class="animal">Vogel</em> und <em '
                    'class="plant">Fagus</em> in Frankfurt.',
                },
            }
        ],
    }


@pytest.fixture
def solr_response_with_geojson_field_only(solr_response_geojson_data):
    documents_restricted_to_geojson_field = solr_response_geojson_data

    new_docs = []
    for doc in documents_restricted_to_geojson_field["response"]["docs"]:
        new_dict = {}
        for key, value in doc.items():
            if key.startswith("_") or key in ["geojson"]:
                new_dict[key] = value
        new_docs.append(new_dict)

    documents_restricted_to_geojson_field["response"]["docs"] = new_docs

    return pysolr.Results(documents_restricted_to_geojson_field)


@pytest.fixture
def solr_response_geojson_data():
    geojson_properties = {
        "type": "Feature",
        "id": "https://www.biofid.de/document/12345/d073lo8ewf",
        "geometry": {"type": "Point", "coordinates": [50.11552, 8.68417]},
        "properties": {
            "date": "1836-01-01",
            "taxa": [
                "https://www.biofid.de/ontologies/Vogel",
                "https://www.biofid.de/ontologies/Fagus",
            ],
            "source-url": "https://www.ub.uni-frankfurt/12345",
            "source-label": "Some article title",
            "source-sentence": '<sentence id="1234">Some text</sentence>',
        },
    }

    return {
        "responseHeader": {"status": 0, "QTime": 0, "params": {"q": "*:*"}},
        "response": {
            "numFound": 1,
            "start": 0,
            "docs": [
                {
                    "id": "https://www.biofid.de/document/12345/d073lo8ewf",
                    "spatial_point": "50.1155,8.6841",
                    "source_url": "https://www.biofid.de/document/12345",
                    "geojson": json.dumps(geojson_properties),
                    "date": "1836-01-01T00:00:00Z",
                    "_version_": 1738881701826789376,
                    "taxons": [
                        "https://www.biofid.de/ontologies/Fagus",
                        "https://www.biofid.de/ontologies/Vogel",
                    ],
                },
            ],
        },
    }
