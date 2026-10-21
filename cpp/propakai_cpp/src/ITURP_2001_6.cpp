/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_2001_6.h"
#include <cmath>


// Rec. ITU-R P.2001-6, Attachment H
// lat0:            latitude of first end of path (degrees) [-90, 90]
// lon0:            longitude of first end of path (degrees) [-180, 180]
// lat1:            latitude of second end of path (degrees) [-90, 90]
// lon1:            longitude of second end of path (degrees) [-180, 180]
// distKm:          distance of an intermediate point from the first end of path (km)
// [out] intermLat: latitude of the intermediate point along the great-circle path (degrees) [-90, 90]
// [out] intermLon: longitude of the intermediate point along the great-circle path(degrees) [-180, 180]
void ITURP_2001_6::GreatCircleIntermediatePoint(double lat0, double lon0, double lat1, double lon1, double distKm, double& intermLat, double& intermLon)
{
constexpr double PI_ON_180 = 0.017453292519943295769;
const double phi_tn = lat0*PI_ON_180;
const double sin_phi_tn = sin(phi_tn);
const double cos_phi_tn = cos(phi_tn);
const double phi_te = lon0*PI_ON_180;
const double phi_rn = lat1*PI_ON_180;
const double sin_phi_rn = sin(phi_rn);
const double cos_phi_rn = cos(phi_rn);
const double phi_re = lon1*PI_ON_180;
const double phi_pnt = distKm/Re;
const double sin_phi_pnt = sin(phi_pnt);
const double cos_phi_pnt = cos(phi_pnt);
double phi_pntn, phi_pnte;
double x1, y1, x2, y2;
double Bt2r, delta_lon, r, s;

	delta_lon = phi_re-phi_te;
	r = sin_phi_tn*sin_phi_rn+cos_phi_tn*cos_phi_rn*cos(delta_lon);
	x1 = sin_phi_rn-r*sin_phi_tn;
	y1 = cos_phi_tn*cos_phi_rn*sin(delta_lon);
	if( fabs(x1) < 1E-9 && fabs(y1) < 1E-9 )
		Bt2r = phi_re;
	else
		Bt2r = atan2(y1, x1);

	s = sin_phi_tn*cos_phi_pnt+cos_phi_tn*sin_phi_pnt*cos(Bt2r);
	phi_pntn = asin(s);
	x2 = cos_phi_pnt-s*sin_phi_tn;
	y2 = cos_phi_tn*sin_phi_pnt*sin(Bt2r);
	if( fabs(x2) < 1E-9 && fabs(y2) < 1E-9 )
		phi_pnte = Bt2r;
	else
		phi_pnte = phi_te+atan2(y2, x2);

	intermLat = phi_pntn/PI_ON_180;
	intermLon = phi_pnte/PI_ON_180;
	if( intermLon < -180)
		intermLon += 360;
	if( intermLon > 180)
		intermLon -= 360;
}

// Rec. ITU-R P.2001-6, Section 3.6 of Annex
// f_GHz:        frequency (GHz)
// [return]: wavelength (m)
double ITURP_2001_6::Wavelength(double f_GHz)
{
	return 1.0E-9*c/f_GHz;
}