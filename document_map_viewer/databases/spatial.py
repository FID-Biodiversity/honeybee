from abc import ABC, abstractmethod

from geojson import Feature, FeatureCollection
from document_map_viewer.commons import Query, SearchFilter


class SpatialDatabase(ABC):
    """An abstract class to handle the communication with a database holding spatial data."""

    @abstractmethod
    def get_data_for_location_id(self, location_id: str) -> Feature:
        """Returns the spatial data on a given location ID."""
        pass

    @abstractmethod
    def search_locations_related_to_query(
        self, query: Query, search_filter: SearchFilter = None
    ) -> FeatureCollection:
        """Returns locations that are contained in documents related to the given query and filter data."""
        pass
