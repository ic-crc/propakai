/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_1511_3.h"
#include <cmath>


const DigitalMap ITURP_1511_3::s_TOPO_map("p1511_3/TOPO.dat",
	+90.125, -(1.0/12.0), 2164, -180.125, +(1.0/12.0), 4324, InterpolationType::Bicubic);

const DigitalMap ITURP_1511_3::s_EGM2008_map("p1511_3/EGM2008.txt",
	+90+(2.0/12.0), -(1.0/12.0), 2165, -180-(2.0/12.0), +1.0/12.0, 4325, InterpolationType::Bicubic);

double ITURP_1511_3::TopographicHeight(double lat, double lon)
{
	return s_TOPO_map.GetValue(lat, lon);
}

double ITURP_1511_3::GeocentricEarthRadius(double geodeticLat)
{
	constexpr double a = s_WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM;
	constexpr double f = s_WGS84_ELLIPSOID_FLATTENING_FACTOR;
	constexpr double b = a * (1.0 - f);

	const double lat_rad = geodeticLat * (s_PI / 180.0);
	const double cos_lat = std::cos(lat_rad);
	const double sin_lat = std::sin(lat_rad);

	constexpr double a2 = a*a;
	constexpr double a4 = a2*a2;
	constexpr double b2 = b*b;
	constexpr double b4 = b2*b2;
	const double cos_lat_2 = cos_lat * cos_lat;
	const double sin_lat_2 = sin_lat * sin_lat;
	const double num = a4*cos_lat_2 + b4*sin_lat_2;
	const double denom = a2*cos_lat_2 + b2*sin_lat_2;

	const double r_km = std::sqrt(num / denom);

	return r_km;
}

double ITURP_1511_3::GeodeticToGeocentricLatitude(double geodeticLat)
{
	constexpr double f = s_WGS84_ELLIPSOID_FLATTENING_FACTOR;

	const double geodetic_lat_rad = geodeticLat * (s_PI / 180.0);
	const double geocentric_lat_rad = std::atan((1.0 - f)*(1.0 - f)*std::tan(geodetic_lat_rad));
	const double geocentric_lat_deg = geocentric_lat_rad * (180.0 / s_PI);

	return geocentric_lat_deg;
}

double ITURP_1511_3::GeocentricToGeodeticLatitude(double geocentricLat)
{
	constexpr double f = s_WGS84_ELLIPSOID_FLATTENING_FACTOR;

	const double geocentric_lat_rad = geocentricLat * (s_PI / 180.0);
	const double geodetic_lat_rad = std::atan(std::tan(geocentric_lat_rad) / ((1.0 - f)*(1.0 - f)));
	const double geodetic_lat_deg = geodetic_lat_rad * (180.0 / s_PI);

	return geodetic_lat_deg;
}

double ITURP_1511_3::GeoidUndulation(double lat, double lon)
{
	return s_EGM2008_map.GetValue(lat, lon);
}

std::tuple<double, double, double> ITURP_1511_3::GeodeticToAer(double latG, double lonG, double hG_km,
                                                               double latS, double lonS, double hS_km)
{
	constexpr double a = s_WGS84_ELLIPSOID_SEMI_MAJOR_AXIS_KM;
	constexpr double f = s_WGS84_ELLIPSOID_FLATTENING_FACTOR;

	// Step 1
	constexpr double deg_to_rad = s_PI / 180.0;
	const double latg_rad = latG * deg_to_rad;
	const double long_rad = lonG * deg_to_rad;
	const double lats_rad = latS * deg_to_rad;
	const double lons_rad = lonS * deg_to_rad;

	const double sin_latg = std::sin(latg_rad);
	const double cos_latg = std::cos(latg_rad);
	const double sin_long = std::sin(long_rad);
	const double cos_long = std::cos(long_rad);
	const double sin_lats = std::sin(lats_rad);
	const double cos_lats = std::cos(lats_rad);
	const double sin_lons = std::sin(lons_rad);
	const double cos_lons = std::cos(lons_rad);

	constexpr double e2 = 2.0*f - f*f;
	constexpr double one_minus_f_2 = (1.0 - f) * (1.0 - f);

	const double ng = a / std::sqrt(1.0 - e2*sin_latg*sin_latg);
	const double ns = a / std::sqrt(1.0 - e2*sin_lats*sin_lats);

	const double xg = (ng + hG_km)*cos_latg*cos_long;
	const double yg = (ng + hG_km)*cos_latg*sin_long;
	const double zg = (ng*one_minus_f_2 + hG_km)*sin_latg;

	const double xs = (ns + hS_km)*cos_lats*cos_lons;
	const double ys = (ns + hS_km)*cos_lats*sin_lons;
	const double zs = (ns*one_minus_f_2 + hS_km)*sin_lats;

	const double x = xs - xg;
	const double y = ys - yg;
	const double z = zs - zg;

	// Step 2
	const double e = -sin_long*x + cos_long*y;
	const double n = -sin_latg*cos_long*x - sin_latg*sin_long*y + cos_latg*z;
	const double u = cos_latg*cos_long*x + cos_latg*sin_long*y + sin_latg*z;

	// Step 3
	constexpr double rad_to_deg = 180.0 / s_PI;
	const double v_deg = std::atan2(u, std::sqrt(e*e + n*n)) * rad_to_deg;
	
	double alpha_deg = std::atan2(e, n) * rad_to_deg;
	if (alpha_deg < 0.0)
		alpha_deg += 360.0;
	
	const double R_km = std::sqrt(x*x + y*y + z*z);

	return {alpha_deg, v_deg, R_km};
}
