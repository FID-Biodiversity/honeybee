import datetime
import json
from typing import Literal, Any, List

from biofid.data.query import escape_solr_input
from geojson import Feature, FeatureCollection
from pysolr import Solr

from document_map_viewer import conf
from document_map_viewer.commons import Query, SearchFilter, DateSpan, Point
from document_map_viewer.databases.spatial import SpatialDatabase

SOLR_FILTER_QUERY_PARAMETER_STRING = "fq"
SOLR_POINT_COORDINATES_PARAMETER_STRING = "pt"
SOLR_CURSOR_PARAMETER_STRING = "cursorMark"
SOLR_MAXIMUM_DISTANCE_FROM_POINT_PARAMETER_STRING = "d"
SOLR_RETURN_FIELDS_PARAMETER_STRING = "fl"
SOLR_DATE_PARAMETER_STRING = "date"

SOLR_NOW_KEYWORD_STRING = "NOW"
SOLR_STAR_WILDCARD_STRING = "*"

COORDINATE_DECIMAL_PRECISION = 6


class SolrSpatialDatabase(SpatialDatabase):
    """Handles the communication with a Solr core holding spatial data."""

    DEFAULT_SEARCH_TERM_CONJUNCTION = "AND"
    PARAMETER_LOCATION_ID_STRING = "id"
    PARAMETER_GEOJSON_STRING = "geojson"

    def __init__(self, database_configuration: dict):
        hostname_parameter_name = conf.DATABASE_HOSTNAME_CONFIGURATION_NAME

        if (
            database_configuration is None
            or database_configuration.get(hostname_parameter_name) is None
        ):
            raise ValueError("The hostname for the spatial database has to be set!")

        solr_url = database_configuration[hostname_parameter_name]

        self._solr_db = Solr(solr_url)
        self.search_term_conjunction_string: str = self.DEFAULT_SEARCH_TERM_CONJUNCTION

    def get_data_for_location_id(self, location_id: str) -> FeatureCollection:
        """Returns a GeoJSON FeatureCollection holding a single Feature with the given `location_id`.
        If no location can be found with the given `location_id`, the Feature list in the FeatureCollection
        is empty.
        """
        query = Query(
            original_raw_string_data=[
                f"{self.PARAMETER_LOCATION_ID_STRING}:{location_id}"
            ]
        )
        return self.search_locations_related_to_query(query)

    def search_locations_related_to_query(
        self, query: Query, search_filter: SearchFilter = None
    ) -> FeatureCollection:
        """Returns a GeoJSON FeatureCollection of all features in the database fitting the given parameters.
        If no Features can be found, the Feature list is empty.
        """
        solr_filter = SearchFilter() if search_filter is None else search_filter
        set_search_filter_default_values(solr_filter)

        solr_parameters = search_filter_to_solr_filter_query(solr_filter)
        query_string = generate_solr_query_string(
            query, self.search_term_conjunction_string
        )

        geojson_feature_list = self.call_db(query=query_string, **solr_parameters)

        return convert_json_to_geojson(geojson_feature_list)

    def call_db(self, query, **kwargs) -> list:
        response = self._solr_db.search(q=query, **kwargs)
        return response.docs


def search_filter_to_solr_filter_query(
    search_filter: SearchFilter, solr_query_parser: Literal["bbox", "geofilt"] = "bbox"
) -> dict:
    """Maps the SearchFilter properties to the solr query parameters.
    For details on the Solr query parsers see:
    https://solr.apache.org/guide/8_8/spatial-search.html#searching-with-query-parsers

    All None value fields will be removed from the result!
    """
    solr_filter_query = {}

    if search_filter.spatial_center is not None:
        add_parameter_to_filter_query(
            parameter_value=f"{{!{solr_query_parser} sfield={conf.MAP_VIEWER_SOLR_GEOSPATIAL_FIELD_NAME}}}",
            solr_parameter_name=SOLR_FILTER_QUERY_PARAMETER_STRING,
            solr_filter_query=solr_filter_query,
            is_value_safe=True,
        )

        escaped_latitude = escape_solr_input(
            str(
                round(
                    search_filter.spatial_center.latitude, COORDINATE_DECIMAL_PRECISION
                )
            )
        )
        escaped_longitude = escape_solr_input(
            str(
                round(
                    search_filter.spatial_center.longitude, COORDINATE_DECIMAL_PRECISION
                )
            )
        )
        add_parameter_to_filter_query(
            parameter_value=f"{escaped_latitude},{escaped_longitude}",
            solr_parameter_name=SOLR_POINT_COORDINATES_PARAMETER_STRING,
            solr_filter_query=solr_filter_query,
        )
        add_parameter_to_filter_query(
            parameter_value=search_filter.radius,
            solr_parameter_name=SOLR_MAXIMUM_DISTANCE_FROM_POINT_PARAMETER_STRING,
            solr_filter_query=solr_filter_query,
        )

    add_parameter_to_filter_query(
        parameter_value=search_filter.cursor,
        solr_parameter_name=SOLR_CURSOR_PARAMETER_STRING,
        solr_filter_query=solr_filter_query,
    )
    add_parameter_to_filter_query(
        parameter_value=search_filter.return_fields,
        solr_parameter_name=SOLR_RETURN_FIELDS_PARAMETER_STRING,
        solr_filter_query=solr_filter_query,
    )

    add_parameter_to_filter_query(
        parameter_value=generate_date_span_solr_filter_query(search_filter.date_span),
        solr_parameter_name=SOLR_DATE_PARAMETER_STRING,
        solr_filter_query=solr_filter_query,
        is_value_safe=True,
    )

    return remove_none_values_from_filter_query(solr_filter_query)


def set_search_filter_default_values(search_filter: SearchFilter) -> None:
    """Adds default query values to a SearchFilter, if they are not set already."""
    set_default(
        name="cursor",
        default=conf.SOLR_DEFAULT_VALUE_CURSOR,
        search_filter=search_filter,
    )
    set_default(
        name="hits_per_page",
        default=conf.SOLR_DEFAULT_VALUE_HITS_PER_PAGE,
        search_filter=search_filter,
    )
    set_default(
        name="radius",
        default=conf.SOLR_DEFAULT_VALUE_RADIUS,
        search_filter=search_filter,
    )
    set_default(
        name="return_fields",
        default=conf.SOLR_DEFAULT_VALUE_RETURN_FIELDS,
        search_filter=search_filter,
    )
    set_default(
        name="spatial_center",
        default=conf.SOLR_DEFAULT_VALUE_SPATIAL_CENTER,
        search_filter=search_filter,
        not_set_value=Point(None, None),
    )


def generate_date_span_solr_filter_query(date_span: DateSpan) -> str:
    """Depending on the available data in DateSpan, an appropriate Solr filter query is generated.
    If either the first or the last year is None, their respective value will be their respective wildcard
    ("*" for `first_year` and "NOW" for last_year).
    """

    def raise_if_not_date_or_none(variable) -> None:
        if variable is not None and not isinstance(variable, datetime.date):
            raise TypeError("The given variable is not a date class!")

    first_year = date_span.first_year
    raise_if_not_date_or_none(first_year)

    last_year = date_span.last_year
    raise_if_not_date_or_none(last_year)

    first_year = first_year if first_year is not None else SOLR_STAR_WILDCARD_STRING
    last_year = last_year if last_year is not None else SOLR_NOW_KEYWORD_STRING

    return f"[{first_year} TO {last_year}]"


def convert_json_to_geojson(feature_list: List[dict]) -> FeatureCollection:
    features = [
        Feature(**json.loads(feature[conf.MAP_VIEWER_SOLR_GEOJSON_DATA_FIELD_NAME]))
        for feature in feature_list
    ]
    return FeatureCollection(features)


def add_parameter_to_filter_query(
    parameter_value: Any,
    solr_parameter_name: str,
    solr_filter_query: dict,
    is_value_safe: bool = False,
) -> None:
    """Adds a given `parameter_value` to the given `solr_filter_query`.
    If `is_value_safe` is False (default), the `parameter_value` will be escaped for Solr input.
    """
    if not is_value_safe:
        parameter_value = escape_solr_input(str(parameter_value))

    if parameter_value is not None:
        solr_filter_query[solr_parameter_name] = parameter_value


def generate_solr_query_string(query: Query, conjunction_term: str) -> str:
    cleaned_conjunction_string = conjunction_term.strip()
    return f" {cleaned_conjunction_string} ".join(query.original_raw_string_data)


def set_default(
    name: str, default: Any, search_filter: SearchFilter, not_set_value: Any = None
) -> None:
    """Sets the given `default` as value for the variable `name`.
    The variable `name` has to be a member of `search_filter`, otherwise an AttributeError is raised.
    The variable value is compared against the `not_set_value` parameter (defaults to None). If the values
    are equal (i.e. on the value level) than default value is set instead.
    """
    current_value = getattr(search_filter, name)
    if current_value == not_set_value:
        setattr(search_filter, name, default)


def remove_none_values_from_filter_query(filter_query: dict) -> dict:
    """Removes all key/value pairs with a None value from the dict.
    Returns a new dict with the result.
    """
    return {key: value for key, value in filter_query.items() if value is not None}
