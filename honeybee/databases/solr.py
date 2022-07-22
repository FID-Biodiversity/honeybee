import datetime
import json
from typing import Any, List, Optional

from biofid.data.query import escape_solr_input
from geojson import Feature, FeatureCollection
from pysolr import Solr

from honeybee import conf
from honeybee.commons import (
    Query,
    SearchFilter,
    DateSpan,
    UserInputException,
)
from honeybee.databases.spatial import SpatialDatabase

SOLR_PARAMETER_NAME_FILTER_QUERY = "fq"
SOLR_PARAMETER_NAME_POINT_COORDINATES = "pt"
SOLR_PARAMETER_NAME_CURSOR = "cursorMark"
SOLR_PARAMETER_NAME_MAXIMUM_DISTANCE_FROM_POINT = "d"
SOLR_PARAMETER_NAME_RETURN_FIELDS = "fl"
SOLR_PARAMETER_NAME_DATE = "date"
SOLR_PARAMETER_NAME_HITS_PER_PAGE = "rows"

SOLR_NOW_KEYWORD_STRING = "NOW"
SOLR_STAR_WILDCARD_STRING = "*"

SOLR_FILTER_QUERY_PARAMETER_NAMES = [
    SOLR_PARAMETER_NAME_DATE,
]


class SolrSpatialDatabase(SpatialDatabase):
    """Handles the communication with a Solr core holding spatial data."""

    DEFAULT_SEARCH_TERM_CONJUNCTION = "OR"
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
        query_string = f"{self.PARAMETER_LOCATION_ID_STRING}:{location_id}"
        geojson_feature = self.call_db(query=query_string)

        return convert_json_to_geojson(geojson_feature)

    def search_locations_related_to_query(
        self, query: Query, search_filter: SearchFilter = None
    ) -> FeatureCollection:
        """Returns a GeoJSON FeatureCollection of all features in the database fitting the given parameters.
        If no Features can be found, the Feature list is empty.
        """
        solr_filter = SearchFilter() if search_filter is None else search_filter
        solr_parameters = search_filter_to_solr_filter_query(solr_filter)

        query.search_string = generate_solr_query_string(
            query, self.search_term_conjunction_string
        )

        geojson_feature_list = self.call_db(
            query=query.search_string, **solr_parameters
        )

        return convert_json_to_geojson(geojson_feature_list)

    def call_db(self, query, **kwargs) -> list:
        response = self._solr_db.search(q=query, **kwargs)
        return response.docs


def search_filter_to_solr_filter_query(search_filter: SearchFilter) -> dict:
    """Maps the SearchFilter properties to the solr query parameters.
    For details on the Solr query parsers see:
    https://solr.apache.org/guide/8_8/spatial-search.html#searching-with-query-parsers

    All string values will be escaped.
    All None value fields and empty list value fields will be removed from the result!

    Default Solr parameters will be set, if the value was not given.
    """
    solr_search_parameters = {}

    if search_filter.spatial_center is not None:
        add_parameter_to_filter_query(
            parameter_value=conf.SOLR_DEFAULT_VALUE_FILTER_QUERY,
            solr_parameter_name=SOLR_PARAMETER_NAME_FILTER_QUERY,
            solr_filter_query=solr_search_parameters,
            is_value_safe=True,
        )

        escaped_latitude = escape_solr_input(
            str(
                round(
                    search_filter.spatial_center.latitude,
                    conf.COORDINATE_DECIMAL_PRECISION,
                )
            )
        )
        escaped_longitude = escape_solr_input(
            str(
                round(
                    search_filter.spatial_center.longitude,
                    conf.COORDINATE_DECIMAL_PRECISION,
                )
            )
        )
        add_parameter_to_filter_query(
            parameter_value=f"{escaped_latitude},{escaped_longitude}",
            solr_parameter_name=SOLR_PARAMETER_NAME_POINT_COORDINATES,
            solr_filter_query=solr_search_parameters,
        )
        add_parameter_to_filter_query(
            parameter_value=search_filter.radius,
            solr_parameter_name=SOLR_PARAMETER_NAME_MAXIMUM_DISTANCE_FROM_POINT,
            solr_filter_query=solr_search_parameters,
        )

    add_parameter_to_filter_query(
        parameter_value=search_filter.cursor,
        solr_parameter_name=SOLR_PARAMETER_NAME_CURSOR,
        solr_filter_query=solr_search_parameters,
    )
    add_parameter_to_filter_query(
        parameter_value=search_filter.return_fields,
        solr_parameter_name=SOLR_PARAMETER_NAME_RETURN_FIELDS,
        solr_filter_query=solr_search_parameters,
    )
    add_parameter_to_filter_query(
        parameter_value=generate_date_span_solr_filter_query(search_filter.date_span),
        solr_parameter_name=SOLR_PARAMETER_NAME_DATE,
        solr_filter_query=solr_search_parameters,
        is_value_safe=True,
    )

    solr_search_parameters = remove_none_values_and_empty_lists_from_filter_query(
        solr_search_parameters
    )
    set_search_parameter_defaults(solr_search_parameters)

    merge_filter_query_parameters(solr_search_parameters)

    return solr_search_parameters


def set_search_parameter_defaults(solr_search_parameters: dict) -> None:
    """Adds default query values to the Solr search parameters, if they are not set already."""
    set_default(
        name=SOLR_PARAMETER_NAME_CURSOR,
        default=conf.SOLR_DEFAULT_VALUE_CURSOR,
        search_parameters=solr_search_parameters,
    )
    set_default(
        name=SOLR_PARAMETER_NAME_HITS_PER_PAGE,
        default=conf.SOLR_DEFAULT_VALUE_HITS_PER_PAGE,
        search_parameters=solr_search_parameters,
    )
    set_default(
        name=SOLR_PARAMETER_NAME_MAXIMUM_DISTANCE_FROM_POINT,
        default=conf.SOLR_DEFAULT_VALUE_RADIUS,
        search_parameters=solr_search_parameters,
    )
    set_default(
        name=SOLR_PARAMETER_NAME_FILTER_QUERY,
        default=conf.SOLR_DEFAULT_VALUE_FILTER_QUERY,
        search_parameters=solr_search_parameters,
    )
    set_default(
        name=SOLR_PARAMETER_NAME_POINT_COORDINATES,
        default=conf.SOLR_DEFAULT_VALUE_SPATIAL_CENTER,
        search_parameters=solr_search_parameters,
    )


def generate_date_span_solr_filter_query(
    date_span: Optional[DateSpan],
) -> Optional[str]:
    """Depending on the available data in DateSpan, an appropriate Solr filter query is generated.
    If either the first or the last year is None, their respective value will be their respective wildcard
    ("*" for `first_year` and "NOW" for last_year).

    If both values are None, None is returned. The same applies of `date_span` is None.
    """
    if date_span is None:
        return None

    def raise_if_not_date_or_none(variable) -> None:
        if variable is not None and not isinstance(variable, datetime.date):
            raise TypeError("The given variable is not a date class!")

    first_year = date_span.first_year
    raise_if_not_date_or_none(first_year)

    last_year = date_span.last_year
    raise_if_not_date_or_none(last_year)

    if first_year is None and last_year is None:
        return None

    first_year = first_year if first_year is not None else SOLR_STAR_WILDCARD_STRING
    last_year = last_year if last_year is not None else SOLR_NOW_KEYWORD_STRING

    return f"[{first_year} TO {last_year}]"


def merge_filter_query_parameters(solr_search_parameters: dict) -> None:
    fq_values = [
        f"{fq_parameter_name}:{solr_search_parameters.pop(fq_parameter_name)}"
        for fq_parameter_name in SOLR_FILTER_QUERY_PARAMETER_NAMES
        if fq_parameter_name in solr_search_parameters
    ]

    fq_value = solr_search_parameters.get(SOLR_PARAMETER_NAME_FILTER_QUERY)
    if fq_value is not None:
        if isinstance(fq_value, (tuple, list)):
            fq_values.extend(fq_value)
        else:
            fq_values.append(fq_value)

    solr_search_parameters[SOLR_PARAMETER_NAME_FILTER_QUERY] = tuple(fq_values)


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
    If `is_value_safe` is False (default), the `parameter_value` will be escaped for Solr input. If `parameter_value`
    is a (non-nested) list, the single list elements will be escaped.
    """
    if parameter_value is not None and not is_value_safe:
        if isinstance(parameter_value, str):
            parameter_value = escape_solr_input(parameter_value)
        elif isinstance(parameter_value, list):
            parameter_value = [escape_solr_input(value) for value in parameter_value]

    if parameter_value is not None:
        solr_filter_query[solr_parameter_name] = parameter_value


def generate_solr_query_string(query: Query, conjunction_term: str) -> str:
    """Generates a solr query string from the given Query object.
    If no query data is given in the Query object, a default value will be set.

    All user input will be escaped in the returned query string.
    Each term will be double quoted in the final query string.
    """

    def escape_and_quote_term(term: str) -> str:
        escaped_term = escape_solr_input(term)
        return f'"{escaped_term}"'

    cleaned_conjunction_string = conjunction_term.strip()

    query_string = f" {cleaned_conjunction_string} ".join(
        escape_and_quote_term(search_term)
        for search_term in query.original_raw_string_data
    )

    if not query_string:
        query_string = conf.SOLR_DEFAULT_VALUE_QUERY_STRING
    else:
        query_string = f"{conf.MAP_VIEWER_SOLR_TERM_SEARCH_FIELD_NAME}:({query_string})"

    return query_string


def set_default(
    name: str, default: Any, search_parameters: dict, not_set_value: Any = None
) -> None:
    """Sets the given `default` as value for the variable `name`.
    If `name` is not in the given `search_parameters`, it will be set with the given default value.
    The key's value is compared against the `not_set_value` parameter (defaults to None). If the values
    are equal (i.e. on the value level) than default value is set instead.
    """
    if name not in search_parameters:
        search_parameters[name] = default
    else:
        current_value = search_parameters[name]
        if current_value == not_set_value:
            search_parameters[name] = default


def remove_none_values_and_empty_lists_from_filter_query(filter_query: dict) -> dict:
    """Removes all key/value pairs with a None value or an empty list from the dict.
    Returns a new dict with the result.
    """
    return {
        key: value for key, value in filter_query.items() if value is not None and value
    }
