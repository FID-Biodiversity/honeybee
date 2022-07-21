import datetime
from dataclasses import dataclass
from typing import Optional

from django.http import QueryDict
from geojson import FeatureCollection, Feature

from document_map_viewer.commons import (
    DateSpan,
    Point,
    Query,
    SearchFilter,
    get_from_data,
)
from document_map_viewer import conf
from document_map_viewer.databases.solr import SolrSpatialDatabase
from document_map_viewer.databases.spatial import SpatialDatabase


def search_spatial_data(raw_url_parameters: QueryDict) -> dict:
    """Searches GeoJSON data in a database for the given parameters."""
    database_configuration = {
        conf.DATABASE_HOSTNAME_CONFIGURATION_NAME: conf.MAP_VIEWER_SOLR_SPATIAL_DATABASE_HOSTNAME
    }

    spatial_search = SpatialSearch(
        spatial_database=SolrSpatialDatabase(database_configuration)
    )

    search_filter = create_search_filter_from_url_parameters(raw_url_parameters)
    query = create_query_from_url_parameters(raw_url_parameters)

    return spatial_search.search(query, search_filter)


@dataclass
class SpatialSearch:
    """A class to retrieve data from a SpatialDatabase."""

    spatial_database: SpatialDatabase

    def search(self, query: Query, search_filter: SearchFilter) -> FeatureCollection:
        """Search spatial data according to the given parameters and return the data as GeoJSON Feature Collection."""
        return self.spatial_database.search_locations_related_to_query(
            query, search_filter
        )

    def get_data_for_id(self, feature_id: str) -> Feature:
        """Searches the Feature data for a given ID."""
        pass


def create_query_from_url_parameters(url_parameters: QueryDict) -> Query:
    """Extracts the relevant data from the parameters and feeds them to a Query object."""
    terms = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_TERM,
        is_list=True,
        optional=True,
    )
    return Query(original_raw_string_data=terms)


def create_search_filter_from_url_parameters(url_parameters: QueryDict) -> SearchFilter:
    """Extract the relevant data from the parameters and feeds them to a SearchFiler object."""
    cursor_token = get_from_data(
        data=url_parameters, name=conf.URL_PARAMETER_NAME_RESUME_TOKEN, optional=True
    )
    hits_per_page = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_HITS_PER_PAGE,
        parameter_type=int,
        optional=True,
    )
    radius = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_RADIUS,
        parameter_type=float,
        optional=True,
    )

    center_point = create_point_from_url_parameter(url_parameters)
    date_span = create_date_span_from_url_parameters(url_parameters)

    mapping = {
        "cursor": cursor_token,
        "date_span": date_span,
        "hits_per_page": hits_per_page,
        "spatial_center": center_point,
        "radius": radius,
    }

    return SearchFilter(**mapping)


def create_date_span_from_url_parameters(url_parameters: QueryDict) -> DateSpan:
    first_year = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_YEAR_START,
        parameter_type=int,
        optional=True,
    )
    last_year = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_YEAR_END,
        parameter_type=int,
        optional=True,
    )

    if first_year is not None:
        first_year = datetime.date(year=first_year, month=1, day=1)

    if last_year is not None:
        last_year = datetime.date(year=last_year, month=1, day=1)

    return DateSpan(first_year=first_year, last_year=last_year)


def create_point_from_url_parameter(url_parameters: QueryDict) -> Optional[Point]:
    """ Creates a Point object from the given URL parameters.
    If only one of the two values, longitude or latitude, is set while the other is None, a ValueError is raised.
    If neither of the two values is set, None is returned.
    """
    longitude = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_LONGITUDE,
        parameter_type=float,
        optional=True,
    )
    latitude = get_from_data(
        data=url_parameters,
        name=conf.URL_PARAMETER_NAME_LATITUDE,
        parameter_type=float,
        optional=True,
    )

    if (longitude is None and latitude is not None) or (longitude is not None and latitude is None):
        raise ValueError('Either both value have to be set or neither.')

    if longitude is None:
        return None

    return Point(longitude=longitude, latitude=latitude)
