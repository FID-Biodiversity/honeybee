# Description

The BIOfid Honeybee Django app provides mainly a REST interface to communicate with a database in the backend to retrieve spatial data in GeoJSON format. Currently, the app relies on Solr being this spatial database, but it is easily possible to implement other databases.

# Installation

Clone and install the repo:

```shell
git clone https://github.com/FID-Biodiversity/honeybee.git
cd honeybee
virtualenv venv
source venv/bin/activate
pip install .
```

In your `settings.py` add `'honeybee'` to your installed app.

## Configuration

You have to provide at least two parameters in your `settings.py`: `MAP_VIEWER_SOLR_SPATIAL_DATABASE_HOSTNAME` and `MAP_VIEWER_SOLR_GEOSPATIAL_FIELD_NAME`. The first should hold the Database endpoint to communicate with. The second is the (Solr) field (or column name in SQL terms) name where the georeference data (aka the coordinates for spatial searches) is stored.

There are also optional parameters:

| Parameter Name | Description | Default Value |
| --- | --- | --- |
| MAP_VIEWER_SOLR_GEOJSON_DATA_FIELD_NAME | The (Solr) field name holding the GeoJSON data (as a string). | 'geojson' |
| MAP_VIEWER_SOLR_TERM_SEARCH_FIELD_NAME | The (Solr) field name holding a list of possible search terms related to the spatial data. | 'taxa' |

# Testing

To install the testing dependencies run `pip install .['dev']` . Subsequently, run `pytest`.

# License
![AGPL-3.0 License](https://www.gnu.org/graphics/agplv3-88x31.png)