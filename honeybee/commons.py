from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Any, Optional, List

from django.http import QueryDict
from honeybee import conf


@dataclass
class DateSpan:
    """Holds a span of dates."""

    first_year: Optional[date]
    last_year: Optional[date]


@dataclass
class Point:
    """Holds simply point data."""

    longitude: float
    latitude: float


@dataclass
class Query:
    """A data holder for all data related to the user query."""

    original_raw_string_data: List[str]
    search_string: str = None


@dataclass
class SearchFilter:
    """Holds all data that is needed to filter a search."""

    cursor: Optional[str] = None
    date_span: Optional[DateSpan] = None
    filter_parameters: List[str] = field(default_factory=list)
    hits_per_page: Optional[int] = None
    radius: Optional[float] = None
    return_fields: List[str] = field(default_factory=list)
    spatial_center: Optional[Point] = None


class UserInputException(Exception):
    """A dedicated exception class for errors that should be returned to the user."""

    pass


def get_from_data(
    data: QueryDict,
    name: str,
    parameter_type: Callable = None,
    is_list: bool = False,
    optional: bool = False,
    default: Any = None,
) -> Any:
    """Accesses the parameter with `name` in the `data` and returns its value.
    If the given `name` is NOT present in `data` and `optional` is True, the `default` is returned.
    In the same scenario, if `optional` is False (default), an LookupError is raised.
    If `parameter_type` is given, the parameter value will be converted into this type. If this is not possible (i.e.
    the parameter value is not of the given type, a ValueError will be raised.
    If `is_list` is True, a list of all parameters of the given `name` will be converted to `parameter_type` (if given)
    and returned in a list.
    This method does NO sanitizing, except for making sure that the requested type is given!
    """
    is_name_in_data = name in data

    if not optional and not is_name_in_data:
        raise UserInputException(f"The parameter '{name}' is missing in the request!")

    parameter_value = (
        data.get(name, default) if not is_list else data.getlist(name, default)
    )

    if parameter_value is not None and parameter_type is not None:
        try:
            if isinstance(parameter_value, list):
                parameter_value = [parameter_type(value) for value in parameter_value]
            else:
                parameter_value = parameter_type(parameter_value)
        except ValueError:
            raise UserInputException(
                conf.ERROR_MESSAGE_INPUT_PARAMETER_HAS_WRONG_FORMAT.format(
                    name=name, parameter_type=parameter_type.__name__
                )
            )

    return parameter_value
