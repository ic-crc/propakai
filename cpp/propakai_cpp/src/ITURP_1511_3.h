/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <tuple>
#include "DigitalMap.h"


class ITURP_1511_3
{
public:
	/**
	 * @brief ITU-R P.1511-3, Annex 1, Section 1.1.
	 * 
	 * Topographic height of the surface of the Earth above mean sea level (m).
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return The topographic height of the surface of the Earth above mean sea level (m).
	 */
	static double TopographicHeight(double lat, double lon);

	/**
	 * @brief Computes the geocentric Earth radius (km) at the specified geodetic latitude.
	 * 
	 * @details Based on ITU-R P.1511-3, Annex 1, Section 2.1.
	 * 
	 * @param geodeticLat Geodetic latitude (degrees).
	 * @return double Geocentric Earth radius (km) at the specified geodetic latitude.
	 */
	static double GeocentricEarthRadius(double geodeticLat);

	/**
	 * @brief For a location on the surface of the WGS 84 reference ellipsoid, converts a geodetic latitude
	 * to a geocentric latitude.
	 * 
	 * @details ITU-R P.1511-3, Annex 1, Section 2.1.
	 * 
	 * @param geodeticLat Geodetic latitude (degrees).
	 * @return double Geocentric latitude (degrees).
	 */
	static double GeodeticToGeocentricLatitude(double geodeticLat);

	/**
	 * @brief For a location on the surface of the WGS 84 reference ellipsoid, converts a geocentric latitude
	 * to a geodetic latitude.
	 * 
	 * @details ITU-R P.1511-3, Annex 1, Section 2.1.
	 * 
	 * @param geocentricLat Geocentric latitude (degrees).
	 * @return double Geodetic latitude (degrees).
	 */
	static double GeocentricToGeodeticLatitude(double geocentricLat);

	/**
	 * @brief ITU-R P.1511-3, Annex 1, Section 1.1.
	 * 
	 * Geoid undulation (m), that is, the height difference between the WGS 84 geoid and the
	 * WGS 84 ellipsoid.
	 * 
	 * @param lat Latitude (degrees), with -90 <= lat <= 90.
	 * @param lon Longitude (degrees), with -180 <= lon <= 180.
	 * @return The Geoid undulation, h_EGM2008 (m), that is, the height difference between the
	 *         WGS 84 geoid and the WGS 84 ellipsoid.
	 */
	static double GeoidUndulation(double lat, double lon);

	/**
	 * @brief Free-space look angles and free-space slant range between two stations in geodetic coordinates
	 * (AER: azimuth-elevation-range).
	 * 
	 * @details ITU-R P.1511-3, Annex 1, Section 3.
	 * 
	 * @param latG Origin geodetic latitude (degrees), with -90 <= latG <= 90.
	 * @param lonG Origin longitude (degrees), with -180 <= lonG <= 180.
	 * @param hG_km Origin height above mean sea level (e.g. above the WGS 84 reference ellipsoid) (km).
	 * @param latS Target geodetic latitude (degrees), with -90 <= latS <= 90.
	 * @param lonS Target longitude (degrees), with -180 <= lonS <= 180.
	 * @param hS_km Target height above mean sea level (e.g. above the WGS 84 reference ellipsoid) (km).
	 * @return std::tuple<double, double, double> 
	 * - [0] a: Free-space geodetic azimuth angle from the origin location to the target location, measured clockwise from geodetic north (degrees).
	 * - [1] v: Free-space geodetic elevation (i.e. the vertical) angle from the origin location to the target location (degrees).
	 * - [2] R: Free-space slant range between the origin location and target location (km).
	 */
	static std::tuple<double, double, double> GeodeticToAer(double latG, double lonG, double hG_km, double latS, double lonS, double hS_km);

protected:
    static constexpr double s_WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM = 6378.137;
    static constexpr double s_WGS84_ELLIPSOID_FLATTENING_FACTOR = 1.0 / 298.257223563;
	static constexpr double s_PI = 3.14159265358979323846;

	static const DigitalMap s_TOPO_map;
	static const DigitalMap s_EGM2008_map;

private:
	// Prevent instantiation
	ITURP_1511_3() = delete;                                 // Delete default constructor
	ITURP_1511_3(const ITURP_1511_3&) = delete;              // Delete copy constructor
	ITURP_1511_3(ITURP_1511_3&&) = delete;                   // Delete move constructor
	ITURP_1511_3& operator=(const ITURP_1511_3&) = delete;   // Delete copy assignment
	ITURP_1511_3& operator=(ITURP_1511_3&&) = delete;        // Delete move assignment
};
