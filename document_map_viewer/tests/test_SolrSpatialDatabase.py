from unittest.mock import Mock

import pytest
from geojson import FeatureCollection

from document_map_viewer.databases.solr import SolrSpatialDatabase


class TestSolrSpatialDatabase:
    def test_get_data_for_id(
        self, solr_spatial_database, single_point_geojson_in_feature_collection
    ):
        solr_spatial_database.call_db.return_value = (
            single_point_geojson_in_feature_collection
        )

        response_data = solr_spatial_database.get_data_for_location_id("123abc")

        assert isinstance(response_data, FeatureCollection)
        solr_spatial_database.call_db.assert_called_with(
            query="id:123abc", fl=["geojson"]
        )

    @pytest.fixture
    def solr_spatial_database(self):
        spatial_database = SolrSpatialDatabase({"url": "http://localhost:1234/solr"})
        spatial_database.call_db = Mock()

        return spatial_database
