from functools import partial

from django.conf import settings

from honeybee.commons import Point

get_setting = partial(getattr, settings)

# URL Parameters
URL_PARAMETER_NAME_FORMAT = 'format'
URL_PARAMETER_NAME_HITS_PER_PAGE = 'hitsPerPage'
URL_PARAMETER_NAME_LATITUDE = 'lat'
URL_PARAMETER_NAME_LONGITUDE = 'lon'
URL_PARAMETER_NAME_RADIUS = 'radius'
URL_PARAMETER_NAME_RESUME_TOKEN = 'resumeToken'
URL_PARAMETER_NAME_YEAR_END = 'yearEnd'
URL_PARAMETER_NAME_YEAR_START = 'yearStart'
URL_PARAMETER_NAME_TERM = 'term'

COORDINATE_DECIMAL_PRECISION = 6

# Spatial Database Configuration
MAP_VIEWER_SOLR_SPATIAL_DATABASE_HOSTNAME = get_setting('MAP_VIEWER_SOLR_SPATIAL_DATABASE_HOSTNAME', None)
MAP_VIEWER_SOLR_GEOSPATIAL_FIELD_NAME = get_setting('MAP_VIEWER_SOLR_GEOSPATIAL_FIELD_NAME', None)
MAP_VIEWER_SOLR_GEOJSON_DATA_FIELD_NAME = get_setting('MAP_VIEWER_SOLR_GEOJSON_DATA_FIELD_NAME', 'geojson')
MAP_VIEWER_SOLR_TERM_SEARCH_FIELD_NAME = get_setting('MAP_VIEWER_SOLR_TERM_SEARCH_FIELD_NAME', 'taxa')

# Error messages
ERROR_MESSAGE_CONTENT_PARAMETER_NAME = 'error-message'
ERROR_MESSAGE_ONLY_SET_EITHER_LON_OR_LAT = 'Either both value have to be set or neither.'
ERROR_MESSAGE_INPUT_PARAMETER_HAS_WRONG_FORMAT = 'The parameter "{name}" is expected to be of type {parameter_type}!'

# Spatial Database Configuration Parameters
DATABASE_HOSTNAME_CONFIGURATION_NAME = 'url'

# Solr Query Default Values
SOLR_DEFAULT_VALUE_QUERY_STRING = '*:*'
SOLR_DEFAULT_VALUE_CURSOR = '*'
SOLR_DEFAULT_VALUE_DATE_SPAN = '[* TO NOW]'
SOLR_DEFAULT_VALUE_FILTER_QUERY = f"{{!bbox sfield={MAP_VIEWER_SOLR_GEOSPATIAL_FIELD_NAME}}}"
SOLR_DEFAULT_VALUE_HITS_PER_PAGE = 100
SOLR_DEFAULT_VALUE_RADIUS = 50
SOLR_DEFAULT_VALUE_RETURN_FIELDS = MAP_VIEWER_SOLR_GEOJSON_DATA_FIELD_NAME
default_spatial_center = Point(latitude=51.16336, longitude=10.44768)
SOLR_DEFAULT_VALUE_SPATIAL_CENTER = f'{default_spatial_center.latitude},{default_spatial_center.longitude}'
