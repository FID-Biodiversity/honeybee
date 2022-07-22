import pytest


@pytest.fixture
def geojson_data_without_properties(geojson_data) -> dict:
    for feature in geojson_data["features"]:
        del feature["properties"]

    return geojson_data


@pytest.fixture
def geojson_data() -> dict:
    """A GeoJson Feature collection containing reference data on annotations in the text."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "https://www.foobar.com/98764.foo/1234/3456/0",
                "geometry": {
                    "type": "Point",
                    "coordinates": [50.983333333333, 11.316666666667],
                },
                "properties": {
                    "radius": 8000.0,
                    "date": "1945-01-01",
                    "taxa": ["https://www.biofid.de/ontologies/Tracheophyta/gbif/1234"],
                    "source": "https://www.foobar.com/98764.foo",
                    "parent-label": "An awesome title: A comment",
                },
            },
            {
                "type": "Feature",
                "id": "https://www.foobar.com/98764.foo/1234/3456/1",
                "geometry": {
                    "type": "Point",
                    "coordinates": [50.11055555555556, 8.682222222222222],
                },
                "properties": {
                    "radius": 3500.0,
                    "date": "1945-01-01",
                    "taxa": ["https://www.biofid.de/ontologies/Tracheophyta/gbif/1234"],
                    "source": "https://www.foobar.com/98764.foo",
                    "parent-label": "An awesome title: A comment",
                },
            },
            {
                "type": "Feature",
                "id": "https://www.foobar.com/98764.foo/7890/77777/0",
                "geometry": {"type": "Point", "coordinates": [53.264543, 9.6245434]},
                "properties": {
                    "radius": 4300.0,
                    "date": "1989-01-01",
                    "taxa": [
                        "https://www.biofid.de/ontologies/Tracheophyta/gbif/99999"
                    ],
                    "source": "https://www.foobar.com/3653541.bar",
                    "parent-label": "Some interesting text about Fagus",
                },
            },
        ],
    }
