# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Implementation of ITU-R P.1144-13.

Quote: Standard & Citation
    If you use this module in technical reports or academic research, please cite this software
    package along with the underlying ITU-R standard:

    * **ITU-R Standard:** International Telecommunication Union (2025).
      *Recommendation ITU-R P.1144-13: Guidelines for the application of numerical methods used in
      propagation methods of Radiocommunication Study Group 3*. Geneva: ITU.
      https://www.itu.int/rec/R-REC-P.1144/en
"""

from array import array
from propakai.types import FloatArray


__all__ = ['square_grid_bilinear_interpolation',
           'bicubic_interpolation',
           'nearest_neighbor_interpolation',
           'load_digital_map']


def square_grid_bilinear_interpolation(grid: FloatArray, num_rows: int, row_size: int,
                                       r: float, c: float) -> float:
    """
    ITU-R P.1144-13, Annex, section 1b.
    Bi-linear interpolation.

    Args:
        grid (types.FloatArray): The square grid to interpolate from. Assumed to be a one-
            dimensional list or array of num_rows*row_size numeric elements.
        num_rows (int): Number of rows in grid.
        row_size (int): Number of elements in a row of grid.
        r (float): Fractional row number (zero-based index).
        c (float): Fractional column number (zero-based index).

    Returns:
        float: Bi-linear interpolated value from grid.
    """
    R = int(r)
    R = max(R, 0)
    R = min(R, num_rows-2)
    C = int(c)
    C = max(C, 0)
    C = min(C, row_size-2)
    I00 = grid[ R    * row_size +  C   ]
    I10 = grid[(R+1) * row_size +  C   ]
    I01 = grid[ R    * row_size + (C+1)]
    I11 = grid[(R+1) * row_size + (C+1)]
    irc = I00*((R+1-r)*(C+1-c)) + I10*((r-R)*(C+1-c)) + I01*((R+1-r)*(c-C)) + I11*((r-R)*(c-C))
    return float(irc)


def bicubic_interpolation(grid: FloatArray, num_rows: int, row_size: int,
                          r: float, c: float) -> float:
    """
    ITU-R P.1144-13, Annex, section 2.
    Bi-cubic interpolation.

    Args:
        grid (types.FloatArray): The square grid to interpolate from. Assumed to be a one-
            dimensional list or array of num_rows*row_size numeric elements.
        num_rows (int): Number of rows in grid.
        row_size (int): Number of elements in a row of grid.
        r (float): Fractional row number (zero-based index).
        c (float): Fractional column number (zero-based index).

    Returns:
        float: Bi-cubic interpolated value from grid.
    """
    R = int(r)-1
    R = max(R, 0)
    R = min(R, num_rows-4)
    C = int(c)-1
    C = max(C, 0)
    C = min(C, row_size-4)
    RI = [0.0]*4
    I = 0
    for ri_index, X in enumerate(range(R, R+4, 1)):
        for j in range(C, C+4, 1):
            RI[ri_index] += grid[(X*row_size)+j]*_K(c-j)
    for ri_index, i in enumerate(range(R, R+4, 1)):
        I += RI[ri_index]*_K(r-i)
    return float(I)


def _K(d: float) -> float:
    a = -0.5
    abs_d = abs(d)
    if abs_d >= 2:
        return 0
    elif abs_d >= 1:
        return a*abs_d*abs_d*abs_d - 5*a*abs_d*abs_d + 8*a*abs_d - 4*a
    else:
        return (a+2)*abs_d*abs_d*abs_d - (a+3)*abs_d*abs_d + 1


def nearest_neighbor_interpolation(grid: FloatArray, num_rows: int, row_size: int,
                                   r: float, c: float) -> float:
    """
    Not part of P.1144-13, added as convenience.
    Nearest-neighbor interpolation.

    Args:
        grid (types.FloatArray): The square grid to interpolate from. Assumed to be a one-
            dimensional list or array of num_rows*row_size numeric elements.
        num_rows (int): Number of rows in grid.
        row_size (int): Number of elements in a row of grid.
        r (float): Fractional row number (zero-based index).
        c (float): Fractional column number (zero-based index).

    Returns:
        float: Nearest-neighbor interpolated value from grid.
    """
    R = round(r)
    R = max(R, 0)
    R = min(R, num_rows-1)
    C = round(c)
    C = max(C, 0)
    C = min(C, row_size-1)
    return float(grid[R*row_size +  C])


def load_digital_map(filename: str, delimiter: str|None=None) -> array:
    """
    ITU-R P.1144-13.

    Reads an ITU digital map file and store its content into an array.

    Args:
        filename (str): The ITU digital map file.
        delimiter (str or None, optional): Delimiter character between values. Defaults to None
            (i.e any sequence of whitespace is considered a delimiter).

    Returns:
        array: Content of the digital map file as a one-dimensional 64-bit float array.
    """
    digital_map_array = array('d')  # 64-bit float
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split(delimiter)
            digital_map_array.extend(float(val) for val in values if val)
    return digital_map_array
