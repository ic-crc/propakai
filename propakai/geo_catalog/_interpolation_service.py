# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Utiliies to query the interpolation service of the ITU-R Geospatial Catalog.

See https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/
"""

import urllib.parse
import urllib.request
import json
import re


__all__ = ['query',
           'int_month_to_str',
           'percent_to_str_v1',
           'percent_to_str_v2']


def query(item_id: str, lat: float, lon: float, parameters: list[str]|None=None,
          values: list[str]|None=None) -> float:
    """
    Sends a request to the the interpolation service of the ITU-R Geospatial Catalog, returns the
    response as float value.
    """
    _validate_query_inputs(item_id, lat, lon, parameters, values)

    BASE_URL = 'https://br-geoportal.itu.int/ITU-R/BR-GeoApi/interpolate/'
    url = BASE_URL+item_id
    params={'lat': float(lat), 'lon': float(lon)}
    if parameters is not None:
        for param_name, value in zip(parameters, values):
            params[param_name] = value
    query_string = urllib.parse.urlencode(params)
    url = f'{url}?{query_string}'
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req, timeout=5) as response:
        status_code = response.getcode()
        MAX_BYTES = 1000
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise RuntimeError('Response too large.')
        response_text = raw.decode('utf-8', errors='replace')
        if 200 <= status_code < 400:
            data = json.loads(response_text)
            if not isinstance(data, dict):
                raise RuntimeError('Unexpected response type (expected JSON object).')
            keys = list(data.keys())
            if len(keys) != 1:
                raise RuntimeError(f'Unexpected JSON object keys: {keys}')
            key = keys[0]
            result_raw = data[key]
            return float(result_raw)
        else:
            raise RuntimeError(f'Request failed with status code {status_code}')


def _validate_query_inputs(item_id: str, lat: float, lon: float, parameters: list[str]|None=None,
                           values: list[str]|None=None) -> None:
    """
    Validates input parameters for query().
    """
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,96}', item_id):
        raise ValueError('Invalid item_id.')

    if not -90 <= float(lat) <= 90:
        raise ValueError('lat is out of range (-90..90).')
    if not -180 <= float(lon) <= 180:
        raise ValueError('lon out of range (-180..180).')

    if parameters is not None:
        if values is None or len(values) != len(parameters):
            raise ValueError('parameters and values must be provided with the same length.')

        for param_name, value in zip(parameters, values):
            if param_name == 'asset':
                if not re.fullmatch(r'[A-Za-z0-9._]{1,24}', value):
                    raise ValueError(f'Invalid asset value {value}.')
            elif param_name == 'month':
                if value not in {'01','02','03','04','05','06','07','08','09','10','11','12'}:
                    raise ValueError(f'Invalid month value {value}.')
            else:
                raise ValueError(f'Unsupported parameter {param_name}.')


def int_month_to_str(month: int) -> str:
    """
    Converts an int (month value from 1 to 12 inclusively) to a 2-characters string to be used for
    querying the interpolation service.
    """
    if month < 1 and month > 12:
        raise ValueError('month must be between 1 and 12 inclusively.')
    return f'{month:02}'


def percent_to_str_v1(p_percent: float, accepted_nominal_values: list[float]) -> str:
    """
    Converts a float percentage to a string to be used for querying the interpolation service.
    Acceptable values for p_percent must be listed in accepted_nominal_values.

    Examples:
        0.01 --> '001'
        0.1  --> '01'
        1    --> '1'
        90   --> '90'
    """
    if p_percent in accepted_nominal_values:
        if p_percent < 0.1:
            s = f'{p_percent:.2f}'
            s = s.replace('.', '')
            return s
        elif p_percent < 1:
            s = f'{p_percent:.1f}'
            s = s.replace('.', '')
            return s
        else:
            s = f'{p_percent:.0f}'
            return s
    else:
        raise ValueError(f'p_percent must be one of: {accepted_nominal_values}.')


def percent_to_str_v2(p_percent: float, accepted_nominal_values: list[float]) -> str:
    """
    Converts a float percentage to a string to be used for querying the interpolation service.
    Acceptable values for p_percent must be listed in accepted_nominal_values.

    Examples:
        0.1  --> '00d10'
        1    --> '01d00'
        90   --> '90d00'
        99.8 --> '99d80'
    """
    if p_percent in accepted_nominal_values:
        s = f'{p_percent:05.2f}'
        s = s.replace('.', 'd')
        return s
    else:
        raise ValueError(f'p_percent must be one of: {accepted_nominal_values}.')


def percent_to_str_v3(p_percent: float, accepted_nominal_values: list[float]) -> str:
    """
    Converts a float percentage to a string to be used for querying the interpolation service.
    Acceptable values for p_percent must be listed in accepted_nominal_values.

    Examples:
        0.1 --> '0.1'
        1   --> '01'
        50  --> '50'
    """
    if p_percent in accepted_nominal_values:
        if p_percent < 1:
            return f'{p_percent:.1f}'
        else:
            return f'{p_percent:02.0f}'
    else:
        raise ValueError(f'p_percent must be one of: {accepted_nominal_values}.')
