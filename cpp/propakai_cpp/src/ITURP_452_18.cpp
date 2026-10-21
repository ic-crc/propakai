/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_452_18.h"
#include "ITURP_1144_13.h"
#include "ITURP_676_13.h"
#include "ITURP_2001_6.h"
#include <cmath>
#include <limits>
#include <algorithm>
#include <vector>


std::vector<double> ITURP_452_18::_DN50_Vect;
std::vector<double> ITURP_452_18::_N050_Vect;

// Initialize from DN50.TXT ITU file
bool ITURP_452_18::Init_DN50(const char* pathname)
{
	return ITURP_1144_13::InitDigitalMap(_DN50_Vect, _DN50_SIZE, pathname);
}

// Initialize from N050.TXT ITU file
bool ITURP_452_18::Init_N050(const char* pathname)
{
	return ITURP_1144_13::InitDigitalMap(_N050_Vect, _N050_SIZE, pathname);
}

// f:          frequency (GHz) [0.1, 50.0]
// p:          required time percentage(s) for which the calculated basic transmission loss is not exceeded (%) [0.001, 50]
// worstMonth: true to indicate an average "worst month" prediction, false to indicate an average annual prediction
// latt:       latitude of interfering station (degrees) [-90, 90]
// lont:       longitude of interfering, positive = East of Greenwich (degrees) [-180, 180]
// latr:       latitude of interfered-with station (degrees) [-90, 90]
// lonr:       longitude of interfered-with station, positive = East of Greenwich (degrees) [-180, 180]
// htg:        interfering station's antenna centre height above ground level (m) [N/A, N/A]
// hrg:        interfered-with station's antenna centre height above ground level (m) [N/A, N/A]
// Gt:         interfering station's antenna gain in the direction of the horizon along the great-circle interference path (dBi)
// Gr:         interfered-with station's antenna gain in the direction of the horizon along the great-circle interference path (dBi)
// vpol:       true to indicate vertical polarization, false to indicate horizontal polarization
// n:          number of profile points
// d:          distance from interferer profile of n points (km) (distance limit of 10000 km)
// h:          terrain height profile of n points (m above mean sea level)
// cc:         clutter category profile of n points (if set to nullptr, OPEN_RURAL is assumed everywhere).
//             cc is not used if a representative clutter height profile is specified via the rch parameter.
// rch:        representative clutter height (m) profile of n points (if set to nullptr, default representative clutter height values
//             associated with clutter categories in cc are used)
// rcz:        radio climatic zone profile of n points (if set to nullptr, INLAND is assumed everywhere)
// dct, dcr:   If at least 75% of the path is over zone B (SEA) two further parameters are required, dct, dcr, giving the distance of
//             the transmitter and the receiver from the coast (km), respectively, in the direction of the other terminal.
//             For a terminal on a ship or sea platform the distance is zero. (If set to ITURP_452_18::AUTO, values are automatically
//             estimated using the radio climate zone (rcz) and distance (d) profiles).
// P:          atmospheric pressure (hPa), default is 1013.25 hPa
// TC:         temperature (°C), default is 15
// deltaN:     average radio-refractivity lapse-rate through the lowest 1 km of the atmosphere (if set to ITURP_452_18::AUTO, its
//             value is automatically obtained from one of the Recommendation's digital map) (N-units/km)
// N0:         sea-level surface refractivity (if set to ITURP_452_18::AUTO, its value is automatically obtained from one of the
//             Recommendation's digital map) (N-units)
// [return]:   basic transmission loss not exceeded for p% time
double ITURP_452_18::ClearAirBasicTransmissionLoss(double f, double p, bool worstMonth, double latt, double lont, double latr, double lonr, 
                                                   double htg, double hrg, double Gt, double Gr, bool vpol, unsigned int n, const double* d, const double* h,
                                                   const ClutterCategory* cc, const double* rch, const RadioClimaticZone* rcz, double dct, double dcr,
                                                   double P, double TC, double deltaN, double N0)
{
std::vector<double> gVector;
const double* g; // g: terrain height (m amsl) + representative clutter height (m) profile of n points
std::vector<double> lopsVector;
const double* lops; // lops: length of path sections profile of n points (km)
double hts; // hts: interferer antenna centre height above mean sea level (m)
double hrs; // hrs: interfered-with antenna centre height above mean sea level (m)
double dn; // dn: great-circle path distance (km)
double centreLat; // centreLat: latitude of the path centre between the interfering and interfered-with stations (degrees)
double centreLon; // centreLon: longitude of the path centre between the interfering and interfered-with stations (degrees)
double aB; // aB: effective Earth radius exceeded for B0 time (km)
double B0; // B0: the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
double ae; // ae: median effective Earth radius (km)
double omega; // omega: the fraction of the total path over water
double dtm; // dtm: longest continuous land (inland + coastal) section of the great-circle path (km)
double dlm; // dlm: longest continuous inland section of the great-circle path (km)
double TK; // TK: temperature (K)

double dlt; // dlt: interferer antenna horizon distance (km)
double dlr; // dlr: interfered-with antenna horizon distance (km)
double thetat; // thetat: interferer horizon elevation angle (mrad)
double thetar; // thetar: interfered-with horizon elevation angle (mrad)
double theta; // theta: path angular distance (mrad)
double hstd; // hstd: modified smooth-Earth surface at the interfering station location for the diffraction model (m amsl)
double hsrd; // hsrd: modified smooth-Earth surface at the interfered-with station location for the diffraction model (m amsl)
double hte; // hte: effective height of the interfering antenna for the ducting/layer-reflection model (m)
double hre; // hre: effective height of the interfered-with antenna for the ducting/layer-reflection model (m)
double hm; // hm: terrain roughness (m)

double Lbfsg; // Lbfsg: basic transmission loss due to free-space propagation and attenuation by atmospheric gases (dB)
double Lb0p; // Lb0p: basic transmission loss not exceeded for time percentage, p%, due to LoS propagation (dB)
double Lb0B; // Lb0B: basic transmission loss not exceeded for time percentage, B0%, due to LoS propagation (dB)
double Ldp; // Ldp: diffraction loss not exceeded for p% time (dB)
double Lbd50; // Lbd50: median basic transmission loss associated with diffraction (dB)
double Lbd; // Lbd: basic transmission loss associated with diffraction not exceeded for p% time (dB)
double Lbs; // Lbs: basic transmission loss due to troposcatter (dB)
double Lba; // Lba: the prediction of the basic transmission loss occurring during periods of anomalous propagation (ducting and layer reflection) (dB)
double Lb; // Lbc: final basic transmission loss not exceeded for p% time (dB)

	dn = d[n-1];
	_gProfile(n, d, h, cc, rch, gVector);
	g = gVector.data();
	_LengthOfPathSectionsProfile(n, d, lopsVector);
	lops = lopsVector.data();
	omega = _OverWaterPercent(dn, n, rcz, lops);
	if( omega >= 0.75 ) // otherwise dct and dcr are not used
	{
		if( _IsAUTO(dct) )
			dct = _Dct(n, rcz, lops);
		if( _IsAUTO(dcr) )
			dcr = _Dcr(n, rcz, lops);
	}
	_LongestContinuousLand(dn, n, rcz, lops, dtm, dlm);
    ITURP_2001_6::GreatCircleIntermediatePoint(latt, lont, latr, lonr, dn/2.0, centreLat, centreLon);
	B0 = _B0(centreLat, dtm, dlm);

	if( worstMonth )
		p = _AnnualEquivalentTimePercent(p, centreLat, omega);
	TK = TC + 273.15;
	if( _IsAUTO(deltaN) )
		deltaN = _DN50(centreLat, centreLon);
	if( _IsAUTO(N0) )
		N0 = _N050(centreLat, centreLon);
	_EffectiveEarthRadius(deltaN, ae, aB);

	hts = h[0] + htg;
	hrs = h[n-1] + hrg;

	_PathProfileParameters(f, htg, hrg, n, d, h, ae, dlt, dlr, thetat, thetar, theta, hstd, hsrd, hte, hre, hm);

	_LoSPropagationLoss(f, p, B0, hts, hrs, dn, dlt, dlr, omega, P, TK, /*out*/Lbfsg, /*out*/Lb0p, /*out*/Lb0B);
	_DiffractionLoss(f, p, B0, hts, hrs, vpol, ae, aB, n, d, g, omega, hstd, hsrd, Lbfsg, Lb0p, /*out*/Ldp, /*out*/Lbd50, /*out*/Lbd);
	Lbs = _TroposcatterLoss(f, p, Gt, Gr, dn, theta, N0, P, TK);
	Lbs = std::max(Lbs, Lbfsg);
	Lba = _DuctingLayerReflectionLoss(f, p, ae, B0, dlm, dn, hts, hrs, dlt, dlr, thetat, thetar, hte, hre, hm, omega, dct, dcr, P, TK);
	Lb =  _OverallPrediction(p, B0, dn, omega, hts, hrs, ae, n, d, h, Lb0p, Lb0B, Ldp, Lbd50, Lba, Lbd, Lbs);

	return Lb;
}

// Get value from the DN50 digital map.
// ITU-R P.452-18, Attachment 1 to Annex 1, Section 2
// lat:      latitude (degrees) [-90.0, 90.0] 
// lon:      longitude (degrees) [-180.0, 180.0]
// [return]: median annual radio-refractivity lapse-rate through the lowest 1 km of the atmosphere (N-units/km)
double ITURP_452_18::_DN50(double lat, double lon)
{
// lat from +90 to -90, lon from 0 to 360 in _DN50 array
const double latInterval = 1.5;
const double lonInterval = 1.5;
const int numRows = 121; // number of points from [-90, 90] latitude deg range, at 1.5 deg intervals: (180/1.5)+1
const int rowSize = 241; // number of points from [0, 360] longitude deg range, at 1.5 deg intervals: (360/1.5)+1
double r,c;

	if( _DN50_Vect.size() != _DN50_SIZE )
		return 45.0; // use reasonable default value

	if( lon < 0 )
		lon += 360;
	r = (90.0 - lat) / latInterval;
	c = lon / lonInterval;
	return ITURP_1144_13::SquareGridBilinearInterpolation(_DN50_Vect.data(), numRows, rowSize, r, c);
}

// Get value from the N050 digital map.
// ITU-R P.452-18, Attachment 1 to Annex 1, Section 2
// lat:      latitude (degrees) [-90.0, 90.0] 
// lon:      longitude (degrees) [-180.0, 180.0]
// [return]: median annual sea-level surface refractivity (N-units)
double ITURP_452_18::_N050(double lat, double lon)
{
// lat from +90 to -90, lon from 0 to 360 in _N050 array
const double latInterval = 1.5;
const double lonInterval = 1.5;
const int numRows = 121; // number of points from [-90, 90] latitude deg range, at 1.5 deg intervals: (180/1.5)+1
const int rowSize = 241; // number of points from [0, 360] longitude deg range, at 1.5 deg intervals: (360/1.5)+1
double r,c;

	if( _N050_Vect.size() != _N050_SIZE )
		return 325.0; // use reasonable default value

	if( lon < 0 )
		lon += 360;
	r = (90.0 - lat) / latInterval;
	c = lon / lonInterval;
	return ITURP_1144_13::SquareGridBilinearInterpolation(_N050_Vect.data(), numRows, rowSize, r, c);
}

// n:                number of profile points
// d:                distance from transmitter profile of n points (km)
// [out] lopsVector: vector of n points containing the length of path sections (km)
void ITURP_452_18::_LengthOfPathSectionsProfile(unsigned int n, const double* d, std::vector<double>& lopsVector)
{
	lopsVector.reserve(n);
	lopsVector.push_back((d[1]-d[0])/2.0);
	for(unsigned int i=1 ; i<n-1 ; i++)
		lopsVector.push_back( (d[i]-d[i-1])/2.0 + (d[i+1]-d[i])/2.0 );
	lopsVector.push_back((d[n-1]-d[n-2])/2.0);
}

// n:        number of profile points
// rcz:      radio climatic zone profile of n points (if set to nullptr, INLAND is assumed)
// lops:     length of path sections profile of n points (km)
// [return]: dct, distance of the transmitter from the coast in the direction of the receiver.
//           For a terminal on a ship or sea platform the distance is zero (km)
double ITURP_452_18::_Dct(unsigned int n, const RadioClimaticZone* rcz, const double* lops)
{
double dct = 0;

	for(unsigned int i=0 ; i<n ; i++)
	{
		if( rcz[i] != RadioClimaticZone::SEA )
			dct += lops[i];
		else
			break;
	}
	return dct;
}

// n:        number of profile points
// rcz:      radio climatic zone profile of n points (if set to nullptr, INLAND is assumed)
// lops:     length of path sections profile of n points (km)
// [return]: dcr, the distance of the receiver from the coast in the direction of the transmitter.
//           For a terminal on a ship or sea platform the distance is zero (km)
double ITURP_452_18::_Dcr(unsigned int n, const RadioClimaticZone* rcz, const double* lops)
{
double dcr = 0;

	for(unsigned int i=0 ; i<n ; i++)
	{
		if( rcz[n-1-i] != RadioClimaticZone::SEA )
			dcr += lops[n-1-i];
		else
			break;
	}
	return dcr;
}

// ITU-R P.452-18, Annex 1, Section 3.2.1
// deltaN:   average radio-refractivity lapse-rate through the lowest 1 km of the atmosphere (N-units/km)
// [out] ae: median value of effective Earth radius for specified path (km)
// [out] aB: effective Earth radius exceeded for B0 time (km)
void ITURP_452_18::_EffectiveEarthRadius(double deltaN, double& ae, double& aB)
{
double constexpr a = 6371.0;
double k50;

	k50 = 157.0 / (157.0 - deltaN);
	ae = k50*a;
	aB = 3.0*a;
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 2)
// pw:       worst-month time percentage for which particular values of basic transmission loss are not exceeded
// lat:      latitude of the path's centre point (degrees) 
// omega:    the fraction of the total path over water
// [return]: p, the annual equivalent time percentage of the worst-month time percentage
double ITURP_452_18::_AnnualEquivalentTimePercent(double pw, double lat, double omega)
{
constexpr double PI_ON_180 = 0.017453292519943295769;
double p;
double absLatDeg = fabs(lat);
double latRad = lat*PI_ON_180;
double GL;

	if( absLatDeg > 45 )
		GL = sqrt(1.1-pow(fabs(cos(2*latRad)), 0.7));
	else
		GL = sqrt(1.1+pow(fabs(cos(2*latRad)), 0.7));
	p = pow(10.0, (log10(pw)+log10(GL)-(0.186*omega)-0.444)/(0.816+(0.078*omega)));
	p = std::max(p, pw/12.0);

	return p; 
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 3)
// Note that formulas are written differently between P.1812-8 and P.452-18 but they are mathematically equivalent.
// lat:      path centre latitude (degrees)
// dtm:      longest continuous land (inland + coastal) section of the great-circle path (km)
// dlm:      longest continuous inland section of the great-circle path (km)
// [return]: B0, the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
double ITURP_452_18::_B0(double lat, double dtm, double dlm)
{
double B0;
double abslat = fabs(lat);
double tau, u1, u4;

	tau = 1 - exp(-0.000412*pow(dlm, 2.41));
	u1 = pow(pow(10.0, -dtm/(16-6.6*tau)) + pow(10.0, -5.0*(0.496+0.354*tau)), 0.2);
	u1 = std::min(u1, 1.0);
	if( abslat <= 70 )
	{
		u4 = pow(u1, -0.935 + 0.0176*abslat);
		B0 = pow(10.0, -0.015*abslat+1.67)*u1*u4;
	}
	else
	{
		u4 = pow(u1, 0.3);
		B0 = 4.17*u1*u4;
	}
	return B0;
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 3)
// dn:        great-circle path distance (km)
// n:         number of profile points
// rcz:       radio climatic zone profile of n points (if set to nullptr, INLAND is assumed)
// lops:      length of path sections profile of n points (km)
// [out] dtm: longest continuous land (inland + coastal) section of the great-circle path (km)
// [out] dlm: longest continuous inland section of the great-circle path (km)
void ITURP_452_18::_LongestContinuousLand(double dn, unsigned int n, const RadioClimaticZone* rcz,
                                          const double* lops, double &dtm, double& dlm)
{
	dtm = 0;
	dlm = 0;
	if( rcz == nullptr )
		dtm = dlm = dn; // assumes INLAND for whole path
	else
	{
	double temp_dtm = 0;
	double temp_dlm = 0;

		for(unsigned int i=0 ; i<n ; i++)
		{
			if( rcz[i] == RadioClimaticZone::INLAND )
			{
				temp_dtm += lops[i];
				temp_dlm += lops[i];
			}
			else if( rcz[i] == RadioClimaticZone::COASTAL_LAND )
			{
				temp_dtm += lops[i];
				dlm = std::max(dlm, temp_dlm);
				temp_dlm = 0;
			}
			else if( rcz[i] == RadioClimaticZone::SEA )
			{
				dtm = std::max(dtm, temp_dtm);
				temp_dtm = 0;
				dlm = std::max(dlm, temp_dlm);
				temp_dlm = 0;
			}
			else // unexpected value, assumes INLAND
			{
				temp_dtm += lops[i];
				temp_dlm += lops[i];
			}
		}
		dtm = std::max(dtm, temp_dtm);
		dlm = std::max(dlm, temp_dlm);
	}
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 4)
// dn:       great-circle path distance between transmit and receive antennas (km)
// n:        number of profile points
// rcz:      radio climatic zone profile of n points (if set to nullptr, INLAND is assumed)
// lops:     length of path sections profile of n points (km)
// [return]: omega, the fraction of the total path over water [0, 1]
double ITURP_452_18::_OverWaterPercent(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops)
{
double db = 0.0; // Aggregate length of the path sections over water (km)
double omega;
unsigned int waterSectionCount = 0;

	if( rcz != nullptr )
	{
		for(unsigned int i=0 ; i<n ; i++)
		{
			if( rcz[i] == RadioClimaticZone::SEA )
			{
				db += lops[i];
				waterSectionCount++;
			}
		}
	}

	if( waterSectionCount == n )
		omega = 1.0; // to make sure omega is set to exacly 1.0
	else
		omega = db/dn;

	return omega;
}

// ITU-R P.452-18, Annex 1, Section 4.1
// f:        frequency (GHz)
// hts:      transmit antenna centre height above mean sea level (m)
// hrs:      receive antenna centre height above mean sea level (m)
// dn:       great-circle path distance (km)
// rho:      water vapour density (g/m3)
// P:        atmospheric pressure (hPa)
// TK:       temperature (K)
// [return]: Ag, the total gaseous absorption (dB)
double ITURP_452_18::_TotalGaseousAbsorption(double f, double hts, double hrs, double dn, double rho, double P, double TK)
{
double Ag;
double dfs, dh;
double yo, yw;

	dh = (hts-hrs)/1000.0;
	dfs = sqrt(dn*dn + dh*dh);
	yo = ITURP_676_13::AttenuationDueToDryAir(f, P, TK, rho);
	yw = ITURP_676_13::AttenuationDueToWaterVapour(f, P, TK, rho);
	Ag = (yo+yw)*dfs;

	return Ag;
}

// ITU-R P.452-18, Annex 1, Section 4.1
// f:           frequency (GHz)
// p:           percentage of average year for which the calculated signal level is exceeded (%)
// B0:          the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
// hts:         transmit antenna centre height above mean sea level (m)
// hrs:         receive antenna centre height above mean sea level (m)
// dn:          great-circle path distance (km)
// dlt:         transmitting antenna horizon distance (km)
// dlr:         receiving antenna horizon distance (km)
// omega:       the fraction of the total path over water
// P:           atmospheric pressure (hPa)
// TK:          temperature (K)
// [out] Lbfsg: basic transmission loss due to free-space propagation and attenuation by atmospheric gases (dB)
// [out] Lb0p:  basic transmission loss not exceeded for time percentage, p%, due to LoS propagation (dB)
// [out] Lb0B:  basic transmission loss not exceeded for time percentage, B0%, due to LoS propagation (dB)
void ITURP_452_18::_LoSPropagationLoss(double f, double p, double B0, double hts, double hrs, double dn, double dlt, double dlr,
                                       double omega, double P, double TK, double& Lbfsg, double& Lb0p, double& Lb0B)
{
double dfs; // distance between the transmit and receive antennas (km)
double deltah = (hts-hrs)/1000.0;
double Esp; // correcton for multipath and focusing effects at p percentage time (dB)
double EsB; // correcton for multipath and focusing effects at B0 percentage time (dB)
double Es = 2.6 * (1 - exp(-(dlt+dlr)/10.0));
double rho = 7.5+(2.5*omega);
double Ag;

	dfs = sqrt(dn*dn + deltah*deltah); 
	Ag = _TotalGaseousAbsorption(f, hts, hrs, dn, rho, P, TK);
	Lbfsg = 92.4 + 20*log10(f) + 20*log10(dfs) + Ag;

	Esp = Es * log10(p/50.0);
	Lb0p = Lbfsg + Esp;

	EsB = Es * log10(B0/50.0);
	Lb0B = Lbfsg + EsB;
}

// ITU-R P.452-18, Annex 1, Section 4.2.1
// f:        frequency (GHz)
// htc:      transmitting antenna height (m)
// hrc:      receiving antenna height (m)
// Ce:       effective Earth curvature (1/km)
// n:        number of profile points
// d:        distance from transmitter profile of n points (km)
// g:        terrain height (m amsl) + representative clutter height (m) profile of n points
// [return]: Bullington diffraction loss (dB)
double ITURP_452_18::_BullingtonDiffractionLoss(double f, double htc, double hrc, double Ce, unsigned int n, const double* d, const double* g)
{
double Lbull;
double dn = d[n-1];
double lambda = ITURP_2001_6::Wavelength(f);
double Stim;
double Str;
double Luc;
double v;

	Stim = std::numeric_limits<double>::lowest();
	for(unsigned int i=1 ; i<n-1 ; i++)
		Stim = std::max(Stim, (g[i] + 500.0*Ce*d[i]*(dn-d[i])-htc)/d[i]);
	Str = (hrc-htc)/dn;

	if( Stim < Str ) // if diffraction path is LoS
	{
	double vmax;
	
		vmax = std::numeric_limits<double>::lowest();
		for(unsigned int i=1 ; i<n-1 ; i++)
			vmax = std::max(vmax, (g[i] + 500.0*Ce*d[i]*(dn-d[i]) - (htc*(dn-d[i])+hrc*d[i])/dn) * sqrt(0.002*dn/(lambda*d[i]*(dn-d[i]))));
		v = vmax;
	}
	else // else diffraction path is transhorizon
	{
	double Srim, dbp, vb;

		Srim = std::numeric_limits<double>::lowest();
		for(unsigned int i=1 ; i<n-1 ; i++)
			Srim = std::max(Srim, (g[i] + 500.0*Ce*d[i]*(dn-d[i])-hrc)/(dn-d[i]));
		dbp = (hrc-htc+Srim*dn)/(Stim+Srim);
		vb = (htc + Stim*dbp - (htc*(dn-dbp)+hrc*dbp)/dn) * sqrt(0.002*dn/(lambda*dbp*(dn-dbp)));
		v = vb;
	}

	if( v <= -0.78 )
		Luc = 0;
	else
		Luc = 6.9 + 20.0*log10(sqrt((v-0.1)*(v-0.1)+1.0)+v-0.1);

	Lbull = Luc + (1.0-exp(-Luc/6.0))*(10.0+0.02*dn);

	return Lbull;
}

// ITU-R P.452-18, Annex 1, Section 4.2.2
// f:        frequency (GHz)
// vpol:     true to indicate vertical polarization, false to indicate horizontal polarization
// dn:       great-circle path distance between transmit and receive antennas (km)
// ap:       general effective Earth radius (km)
// omega:    the fraction of the total path over water
// htesph:   effective transmitting antenna height (m)
// hresph:   effective receiving antenna height (m)
// [return]: spherical Earth diffraction loss (dB)
double ITURP_452_18::_SphericalEarthDiffractionLoss(double f, bool vpol, double dn, double ap, double omega, double htesph, double hresph)
{
double Ldsph;
double dlos;

	dlos = sqrt(2*ap)*(sqrt(0.001*htesph)+sqrt(0.001*hresph));

	if( dn >= dlos )
		Ldsph = _FirstTermSphericalEarthDiffractionLoss(f, vpol, dn, ap, omega, htesph, hresph);
	else
	{
	constexpr double PI = 3.14159265358979323846;
	double b, c_, mc;
	double dse1, dse2;
	double hse, hreq;

		mc = 250.0*dn*dn/(ap*(htesph+hresph));
		c_ = (htesph-hresph)/(htesph+hresph);
		b = 2.0*sqrt((mc+1.0)/(3.0*mc)) * cos(PI/3.0 + 1.0/3.0 * acos(3.0*c_/2.0*sqrt(3.0*mc/((mc+1.0)*(mc+1.0)*(mc+1.0)))));
		dse1 = dn*(1.0+b)/2.0;
		dse2 = dn-dse1;
		hse = ((htesph-500.0*dse1*dse1/ap)*dse2 + (hresph-500.0*dse2*dse2/ap)*dse1)/dn;
		hreq = 17.456*sqrt(dse1*dse2*ITURP_2001_6::Wavelength(f)/dn);

		if( hse > hreq )
			Ldsph = 0;
		else
		{
		double aem, x;
		double Ldft;

			x = dn/(sqrt(htesph)+sqrt(hresph));
			aem = 500.0*x*x;
			Ldft = _FirstTermSphericalEarthDiffractionLoss(f, vpol, dn, aem, omega, htesph, hresph);
			if( Ldft < 0 )
				Ldsph = 0;
			else
				Ldsph = (1.0-(hse/hreq))*Ldft;
		}
	}

	return Ldsph;
}

// ITU-R P.452-18, Annex 1, Section 4.2.2.1
// f:        frequency (GHz)
// vpol:     true to indicate vertical polarization, false to indicate horizontal polarization
// dn:       great-circle path distance between transmit and receive antennas (km)
// adft:     effective Earth radius (km)
// omega:    the fraction of the total path over water
// htesph:   effective transmitting antenna height (m)
// hresph:   effective receiving antenna height (m)
// [return]: first term spherical Earth diffraction loss (dB)
double ITURP_452_18::_FirstTermSphericalEarthDiffractionLoss(double f, bool vpol, double dn, double adft, double omega, double htesph, double hresph)
{
double Ldftland = 0;
double Ldftsea = 0;
double Ldft;

	if( omega != 1.0 )
		Ldftland = _FirstTermSubCalculation(f, vpol, dn, adft, 22.0, 0.003, htesph, hresph);
	if( omega != 0.0 )
		Ldftsea = _FirstTermSubCalculation(f, vpol, dn, adft, 80.0, 5.0, htesph, hresph);
	Ldft = omega*Ldftsea + (1.0-omega)*Ldftland;

	return Ldft;
}

// ITU-R P.452-18, Annex 1, Section 4.2.2.1
// f:        frequency (GHz)
// vpol:     true to indicate vertical polarization, false to indicate horizontal polarization
// dn:       great-circle path distance between transmit and receive antennas (km)
// adft:     effective Earth radius (km)
// perm:     terrain relative permittivity
// conduct:  terrain conductivity (S/m)
// htesph:   effective transmitting antenna height (m)
// hresph:   effective receiving antenna height (m)
// [return]: first term spherical Earth diffraction loss (dB)
double ITURP_452_18::_FirstTermSubCalculation(double f, bool vpol, double dn, double adft, double perm, double conduct, double htesph, double hresph)
{
double Ldft;
double K, K2, K4;
double Bdft;
double X, Fx, Yt, Yr;

	K = 0.036*pow(adft*f, -1.0/3.0)*pow((perm-1.0)*(perm-1.0) + (18.0*conduct/f)*(18.0*conduct/f), -0.25);
	if( vpol == true )
		K *= sqrt(perm*perm + (18.0*conduct/f)*(18.0*conduct/f));
	
	K2 = K*K;
	K4 = K2*K2;
	Bdft = (1.0 + 1.6*K2 + 0.67*K4)/(1.0 + 4.5*K2 + 1.53*K4);

	X = 21.88*Bdft*pow(f/(adft*adft), 1.0/3.0)*dn;

	Yt = Yr = 0.9575*Bdft*pow(f*f/adft, 1.0/3.0);
	Yt *= htesph;
	Yr *= hresph;

	if( X >= 1.6 )
		Fx = 11.0 + 10.0*log10(X)-17.6*X;
	else
		Fx = -20.0*log10(X)-5.6488*pow(X, 1.425);

	auto G = [Bdft, K] (double Y) -> double
	{
	double B = Bdft*Y;
	double GY;

		if( B > 2 )
			GY = 17.6*sqrt(B-1.1)-5.0*log10(B-1.1)-8.0;
		else
			GY = 20.0*log10(B+0.1*B*B*B);

		GY = std::max(GY, 2.0+20.0*log10(K));
		return GY;
	};

	Ldft = -Fx - G(Yt) - G(Yr);
	return Ldft;
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 4)
// n:             number of profile points
// d:             distance from interferer profile of n points (km)
// h:             terrain height profile of n points (m above mean sea level)
// cc:            clutter category profile of n points
// rch:           representative clutter height profile of n points (m)
// [out] gVector: vector of terrain height (m amsl) + representative clutter height (m) of n elements
void ITURP_452_18::_gProfile(unsigned int n, const double* d, const double* h, const ClutterCategory* cc,
                             const double* rch, std::vector<double>& gVector)
{
double dn = d[n-1];
double graceDistKm = 0.050;
double openRuralRepHeight = _reprHeight(ClutterCategory::OPEN_RURAL);

	gVector.reserve(n);
	gVector.push_back(h[0]);
	for(unsigned int i=1 ; i<n-1 ; i++)
	{
		double gi = h[i];
		if( !(d[i] < graceDistKm || d[i] > dn-graceDistKm) )
		{
			if( rch != nullptr )
				gi += rch[i];
			else if( cc != nullptr )
				gi += _reprHeight(cc[i]);
			else
				gi += openRuralRepHeight;
		}
		gVector.push_back(gi);
	}
	gVector.push_back(h[n-1]);
}

// ITU-R P.452-18, Annex 1, Section 3.2.1 (Step 4, TABLE 3)
double ITURP_452_18::_reprHeight(ClutterCategory cc)
{
	switch (cc)
	{
	case WATER_SEA:
		return 0.0;
	case OPEN_RURAL:
		return 0.0;
	case SUBURBAN:
		return 10.0;
	case URBAN_TREES_FOREST:
		return 15.0;
	case DENSE_URBAN:
		return 20.0;
	default:
		return 0.0;
	}
}

// ITU-R P.452-18, Annex 1, Section 4.2.3
// f:        frequency (GHz)
// htc:      transmitting antenna height (m)
// hrc:      receiving antenna height (m)
// vpol:     true to indicate vertical polarization, false to indicate horizontal polarization
// ap:       general effective Earth radius (km)
// Ce:       effective Earth curvature (1/km)
// n:        number of profile points
// d:        distance from transmitter profile of n points (km)
// g:        terrain height (m amsl) + representative clutter height (m) profile of n points
// omega:    fraction of the total path over water
// hstd:     modified smooth-Earth surface at the transmitting station location (m amsl)
// hsrd:     modified smooth-Earth surface at the receiving station location (m amsl)
// [return]: Complete "delta-Bullington" diffraction loss (dB)
double ITURP_452_18::_DeltaBullingtonDiffractionLoss(double f, double htc, double hrc, bool vpol, double ap, double Ce, unsigned int n, const double* d,
                                                     const double* g, double omega, double hstd, double hsrd)
{
double Lbulla, Lbulls, Ldsph, Ld;
double htcPrime, hrcPrime;
std::vector<double> g0Vector(n, 0.0);
const double* g0 = g0Vector.data();

	Lbulla = _BullingtonDiffractionLoss(f, htc, hrc, Ce, n, d, g);
	htcPrime = htc - hstd;
	hrcPrime = hrc - hsrd;
	Lbulls = _BullingtonDiffractionLoss(f, htcPrime, hrcPrime, Ce, n, d, g0);
	Ldsph = _SphericalEarthDiffractionLoss(f, vpol, d[n-1], ap, omega, htcPrime, hrcPrime);
	Ld = Lbulla + std::max(Ldsph-Lbulls, 0.0);
	return Ld;
}

// ITU-R P.452-18, Annex 1, Section 4.2.4
// f:           frequency (GHz)
// p:           percentage of average year for which the calculated basic transmission loss is not exceeded (%)
// B0:          the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
// htc:         transmitting antenna height (m)
// hrc:         receiving antenna height (m)
// vpol:        true to indicate vertical polarization, false to indicate horizontal polarization
// ae:          median effective Earth radius (km)
// aB:          effective Earth radius exceeded for B0 time (m)
// n:           number of profile points
// d:           distance from transmitter profile of n points (km)
// g:           terrain height (m amsl) + representative clutter height (m) profile of n points
// omega:		fraction of the total path over water
// hstd:        modified smooth-Earth surface at the transmitting station location (m amsl)
// hsrd:        modified smooth-Earth surface at the receiving station location (m amsl)
// Lbfs:        basic transmission loss due to free-space propagation (dB)
// Lb0p:        basic transmission loss not exceeded for time percentage, p%, due to LoS propagation (dB)
// [out] Ldp:   diffraction loss not exceeded for p% time (dB)
// [out] Lbd50: median basic transmission loss associated with diffraction (dB)
// [out] Lbd:   basic transmission loss associated with diffraction not exceeded for p% time (dB)
void ITURP_452_18::_DiffractionLoss(double f, double p, double B0, double htc, double hrc, bool vpol, double ae, double aB, unsigned int n, const double* d,
                                    const double* g, double omega, double hstd, double hsrd, double Lbfs, double Lb0p, double& Ldp, double& Lbd50, double& Lbd)
{
double Ld50;

	Ld50 = _DeltaBullingtonDiffractionLoss(f, htc, hrc, vpol, ae, 1.0/ae, n, d, g, omega, hstd, hsrd);

	if( p > 49.99 && p < 50.01 ) // if roughly evaluates to 50%
		Ldp = Ld50;
	else
	{
	double LdB, Fi;

		LdB = _DeltaBullingtonDiffractionLoss(f, htc, hrc, vpol, aB, 1.0/aB, n, d, g, omega, hstd, hsrd);
		if( p > B0 )
			Fi = _I(p/100.0)/_I(B0/100.0);
		else
			Fi = 1;
		Ldp = Ld50 + (LdB-Ld50)*Fi;
	}

	Lbd50 = Lbfs + Ld50;

	Lbd = Lb0p + Ldp;
}

// ITU-R P.452-18, Annex 1, Section 4.3
// f:        frequency (GHz)
// p:        percentage of average year for which the calculated signal level is exceeded (%) [0.001, 50.0]
// Gt:       transmitter antenna gain in the direction of the horizon along the great-circle interference path (dBi)
// Gr:       receiver antenna gain in the direction of the horizon along the great-circle interference path (dBi)
// dn:       great-circle path distance between transmit and receive antennas (km)
// theta:    path angular distance (mrad)
// N0:       sea-level surface refractivity (N-units)
// P:        atmospheric pressure (hPa)
// TK:       temperature (K)
// [return]: Lbs, basic transmission loss due to troposcatter (dB)
double ITURP_452_18::_TroposcatterLoss(double f, double p, double Gt, double Gr, double dn, double theta, double N0, double P, double TK)
{
double Lf, Lbs, Lc, Ag;

	Lf = 25.0*log10(f) - 2.5*log10(f/2.0)*log10(f/2.0);
	Lc = 0.051*exp(0.055*(Gt+Gr));

	// Note: The official ITU reference implementation only uses hts and hrs in Ag's calculation
	//       for the line-of-sight propagation losses. It is not that clear from the recommendation
	//       document itself whether hts and hrs should be used here ; in any case, the impact on the
	//       overall result is negligible.
	Ag = _TotalGaseousAbsorption(f, 0 /*hts*/, 0 /*hrs*/, dn, 3.0, P, TK);

	Lbs = 190.0 + Lf + 20.0*log10(dn) + 0.573*theta - 0.15*N0 + Lc + Ag - 10.1*pow(-log10(p/50.0), 0.7);

	return Lbs;
}

// ITU-R P.452-18, Annex 1, Section 4.4
// f:            frequency (GHz)
// p:            percentage of average year for which the calculated signal level is exceeded (%)
// ae:           median effective Earth radius (km)
// B0:           the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
// dlm:          longest continuous inland section of the great-circle path (km)
// dn:           great-circle path distance (km)
// hts:          transmit antenna centre height above mean sea level (m)
// hrs:          receive antenna centre height above mean sea level (m)
// dlt:          transmitting antenna horizon distance (km)
// dlr:          receiving antenna horizon distance (km)
// thetat:       transmit horizon elevation angle (mrad)
// thetar:       receive horizon elevation angle (mrad)
// hte:          effective height of the transmitting antenna for the ducting/layer-reflection model (m)
// hre:          effective height of the receiving antenna for the ducting/layer-reflection model (m)
// hm:           terrain roughness (m)
// omega:        fraction of the total path over water
// dct:          distance of the transmitter from the coast in the direction of the receiver. For a terminal on a ship or sea platform the distance is zero (km)
// dcr:          distance of the receiver from the coast in the direction of the transmitter. For a terminal on a ship or sea platform the distance is zero (km)
// P:            atmospheric pressure (hPa)
// TK:           temperature (K)
// [return] Lba: basic transmission loss associated with ducting/layer-reflection not exceeded for p% time (dB)
double ITURP_452_18::_DuctingLayerReflectionLoss(double f, double p, double ae, double B0, double dlm, double dn, double hts, double hrs,
                                                 double dlt, double dlr, double thetat, double thetar, double hte, double hre, double hm,
                                                 double omega, double dct, double dcr, double P, double TK)
{
double thetaPPt, thetaPPr, Af, Adp, Alf, Ast, Asr, Act, Acr;
double yd, Ap, gamma, thetaP, thetaPt, thetaPr, B, logB, tau, u2, u3, alpha;
double Ag, rho;
double Lba;

	// calculations for Af
	thetaPPt = thetat - 0.1*dlt;
	thetaPPr = thetar - 0.1*dlr;
	Ast = Asr = 0.0;
	if( thetaPPt > 0 )
		Ast = 20.0*log10(1.0+0.361*thetaPPt*sqrt(f*dlt))+0.264*thetaPPt*pow(f, 1.0/3.0);
	if( thetaPPr > 0 )
		Asr = 20.0*log10(1.0+0.361*thetaPPr*sqrt(f*dlr))+0.264*thetaPPr*pow(f, 1.0/3.0);
	Act = Acr = 0.0;
	if( omega >= 0.75 )
	{
		if( dct <= dlt && dct <= 5.0 )
			Act = -3.0*exp(-0.25*dct*dct)*(1.0+tanh(0.07*(50.0-hts)));
		if( dcr <= dlr && dcr <= 5.0 )
			Acr = -3.0*exp(-0.25*dcr*dcr)*(1.0+tanh(0.07*(50.0-hrs)));
	}
	Alf = 0.0;
	if( f < 0.5 )
		Alf = 45.375 - 137.0*f + 92.5*f*f;
	Af = 102.45 + 20.0*log10(f) +20.0*log10(dlt+dlr) + Alf + Ast + Asr + Act + Acr;

	// calulations for Ad(p)
	yd = 0.00005*ae*pow(f, 1.0/3.0);
	thetaPt = thetat;
	thetaPr = thetar;
	if( thetat > 0.1*dlt )
		thetaPt = 0.1*dlt;
	if( thetar > 0.1*dlr )
		thetaPr = 0.1*dlr;
	thetaP = 1000.0*dn/ae + thetaPt + thetaPr;
	tau = 1 - exp(-0.000412*pow(dlm, 2.41));
	alpha = -0.6-tau*pow(dn, 3.1)*3.5E-9;
	alpha = std::max(alpha, -3.4);
	u2 = pow(500.0/ae*dn*dn/std::pow(sqrt(hte)+sqrt(hre), 2), alpha);
	u2 = std::min(u2, 1.0);
	u3 = 1.0;
	if( hm > 10.0 )
	{
		double dI = std::min(dn-dlt-dlr, 40.0);
		u3 = exp(-4.6E-5*(hm-10.0)*(43.0+6.0*dI));
	}
	B = B0*u2*u3;
	logB = log10(B);
	gamma = 1.076/pow(2.0058-logB, 1.012)*exp(-(9.51-4.8*logB+0.198*logB*logB)*1.0E-6*pow(dn, 1.13));
	Ap = -12.0+(1.2+0.0037*dn)*log10(p/B)+12.0*pow(p/B, gamma);
	Adp = yd*thetaP + Ap;

	// Note: The official ITU reference implementation only uses hts and hrs in Ag's calculation
	//       for the line-of-sight propagation losses. It is not that clear from the recommendation
	//       document itself whether hts and hrs should be used here ; in any case, the impact on the
	//       overall result is negligible.
	rho = 7.5+(2.5*omega);
	Ag = _TotalGaseousAbsorption(f, 0 /*hts*/, 0 /*hrs*/, dn, rho, P, TK);

	Lba = Af + Adp + Ag;

	return Lba;
}

// ITU-R P.452-18, Annex 1, Section 4.5
// p:        percentage of average year for which the calculated signal level is exceeded (%) [1.0, 50.0]
// B0:       the time percentage for which refractivity lapse-rates exceeding 100 N-units/km can be expected in the first 100 m of the lower atmosphere (%)
// dn:       great-circle path distance between transmit and receive antennas (km)
// omega:    fraction of the total path over water
// htc:      transmitting (interferer) antenna height (m)
// hrc:      receiving (interfered-with) antenna height (m)
// ae:       median effective Earth radius (km)
// n:        number of profile points
// d:        distance from transmitter profile of n points (km)
// h:        terrain height profile of n points (m amsl)
// Lb0p:     notional LoS basic transmission loss not exceeded for p% time (dB)
// Lb0B:     notional LoS basic transmission loss not exceeded for B0% time (dB)
// Ldp:      diffraction loss not exceeded for p% time (dB)
// Lbd50:    median basic transmission loss associated with diffraction (dB)
// Lba:      ducting/layer-reflection basic transmission loss not exceeded for for p% time (dB)
// Lbd:      basic transmission loss for diffraction not exceeded for p% time (dB)
// Lbs:      basic transmission loss due to troposcatter (dB)
// [return]: Lb, basic transmission loss not exceeded for p% time and 50% locations (dB)
double ITURP_452_18::_OverallPrediction(double p, double B0, double dn, double omega, double htc, double hrc, double ae, 
                                        unsigned int n, const double* d, const double* h, double Lb0p, double Lb0B, double Ldp,
                                        double Lbd50, double Lba, double Lbd, double Lbs)
{
double Fj, Stim, Str;
double Ce = 1.0/ae;
double Fi;
double Lminb0p, Lminbap, Lbda, Lbam, Lb;

	Stim = std::numeric_limits<double>::lowest();
	for(unsigned int i=1 ; i<n-1 ; i++)
		Stim = std::max(Stim, (h[i] + 500.0*Ce*d[i]*(dn-d[i])-htc)/d[i]);
	Str = (hrc-htc)/dn;
	Fj = 1.0-0.5*(1.0+tanh(3.0*0.8*(Stim-Str)/0.3));

	if( p < B0 )
		Lminb0p = Lb0p + (1.0-omega)*Ldp;
	else
	{
		if( p > B0 )
			Fi = _I(p/100.0)/_I(B0/100.0);
		else
			Fi = 1;
		Lminb0p = Lbd50 + (Lb0B + (1.0-omega)*Ldp - Lbd50)*Fi;
	}

	Lminbap = 2.5*log(exp(Lba/2.5)+exp(Lb0p/2.5));

	if( Lminbap > Lbd )
		Lbda = Lbd;
	else
	{
		double Fk = 1.0-0.5*(1.0+tanh(3.0*0.5*(dn-20.0)/20.0));
		Lbda = Lminbap + (Lbd-Lminbap)*Fk;
	}

	Lbam = Lbda + (Lminb0p-Lbda)*Fj;

	Lb  = -5.0*log10(pow(10.0, -0.2*Lbs)+pow(10.0, -0.2*Lbam));

	return Lb;
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 4 & 5
// f:            frequency (GHz)
// htg:          transmit antenna centre height above ground level (m)
// hrg:          receive antenna centre height above ground level (m)
// n:            number of profile elements
// d:            distance from transmitter profile of n elements (km)
// h:            terrain height profile of n elements (m above mean sea level)
// ae:           median effective Earth radius (km)
// [out] dlt:    transmitting antenna horizon distance (km)
// [out] dlr:    receiving antenna horizon distance (km)
// [out] thetat: transmit horizon elevation angle (mrad)
// [out] thetar: receive horizon elevation angle (mrad)
// [out] theta:  path angular distance (mrad)
// [out] hstd:   modified hst for the diffraction model (m amsl)
// [out] hsrd:   modified hsr for the diffraction model (m amsl)
// [out] hte:    effective height of the transmitting antenna for the ducting/layer-reflection model (m)
// [out] hre:    effective height of the receiving antenna for the ducting/layer-reflection model (m)
// [out] hm:     terrain roughness (m)
void ITURP_452_18::_PathProfileParameters(double f, double htg, double hrg, unsigned int n,const double* d, const double* h, double ae,
                                          double& dlt, double& dlr, double& thetat, double& thetar, double& theta, double& hstd, double& hsrd,
                                          double& hte, double& hre, double& hm)
{
double hts = h[0] + htg;
double hrs = h[n-1] + hrg;
double dn = d[n-1];
double theta_max, theta_td;
unsigned int theta_max_dist_index;
unsigned int ilt; // index of the profile point at distance dlt from the transmitter
unsigned int ilr; // index of the profile point at distance dlr from the receiver
bool isLoS;
double hst, hsr;

	_MaxTxToTerrainElevationAngle(hts, n, d, h, ae, theta_max, theta_max_dist_index);
	theta_td = _ElevationAngle(hts, hrs, dn, ae); // elevation angle from the transmit to the receive antenna (mrad)
	isLoS = !(theta_max > theta_td);
	thetat = std::max(theta_max, theta_td);
	if( isLoS == false )
		ilt = theta_max_dist_index;
	else
	{
	double Ce = 1.0/ae; // section 3.8 of Annex 1 mentions to use ae for the path profile analysis

		ilt = _LoSMaxDiffractionDist(f, hts, hrs, n, d, h, Ce);
	}
	dlt = d[ilt];

	if( isLoS == true )
	{
		thetar = _ElevationAngle(hrs, hts, dn, ae); // elevation angle from the receive to the transmit antenna (mrad)
		dlr = dn - dlt;
		ilr = ilt;
	}
	else
	{
		_MaxRxToTerrainElevationAngle(hrs, n, d, h, ae, thetar, ilr);
		dlr = dn - d[ilr];
	}

	theta = (1000*dn/ae) + thetat + thetar;

	_SmoothEarthHeights(n, d, h, hst, hsr);
	_SmoothEarthHeightsForDiffractionModel(hts, hrs, n, d, h, hst, hsr, hstd, hsrd);
	_EffectiveHeightsAndTerrainRoughness(htg, hrg, n, d, h, hst, hsr, ilt, ilr, hte, hre, hm);
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 4 & 5.1.3
// hamsl_from: height of location from which the elevation angle is to be calculated (m above mean sea level)
// hamsl_to:   height of location to which the elevation angle is to be calculated (m above mean sea level)
// distKm:     great-circle path distance between the two aforementioned locations (km)
// ae:         median effective Earth radius (km)
// [return]:   elevation angle above local horizontal (mrad)
double ITURP_452_18::_ElevationAngle(double hamsl_from, double hamsl_to, double distKm, double ae)
{
double theta = 1000.0*atan(((hamsl_to-hamsl_from)/(1000.0*distKm))-(distKm/(2.0*ae)));

	return theta;
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 4
// hts:             transmit antenna height above mean sea level (m)
// n:               number of profile elements
// d:               distance from transmitter profile of n elements (km)
// h:               terrain height profile of n elements (m above mean sea level)
// ae:              median effective Earth radius (km)
// [out] theta_max: physical horizon elevation angle as seen by the transmitting antenna (relative to the local horizontal) (mrad)
//                  i.e. maximum elevation angle from transmitter antenna to terrain elements
// [out] dindex:    index of distance to transmitter profile d for which theta_max was found.
void ITURP_452_18::_MaxTxToTerrainElevationAngle(double hts, unsigned int n, const double* d, const double* h,
                                                 double ae, double& theta_max, unsigned int& dindex)
{
	theta_max = std::numeric_limits<double>::lowest();
	dindex = 0;
	for(unsigned int i=1 ; i<n-1 ; i++) // excludes transmit and receive locations
	{
		double theta_i = _ElevationAngle(hts, h[i], d[i], ae);
		if( theta_i > theta_max )
		{
			theta_max = theta_i;
			dindex = i;
		}
	}
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 5.1.2
// f:        frequency (GHz)
// hts:      transmit antenna height above mean sea level (m)
// hrs:      receive antenna height above mean sea level (m)
// n:        number of profile elements
// d:        distance from transmitter profile of n elements (km)
// h:        terrain height profile of n elements (m above mean sea level)
// Ce:       effective Earth curvature (1/km)
// [return]: index of distance to transmitter profile d for which the maximum diffraction parameter was calculated.
unsigned int ITURP_452_18::_LoSMaxDiffractionDist(double f, double hts, double hrs, unsigned int n, const double* d, const double *h, double Ce)
{
double dn = d[n-1];
double vmax = std::numeric_limits<double>::lowest();
double dindex = 0;

	for(unsigned int i=1 ; i<n-1 ; i++) // excludes transmit and receive locations
	{
		double di = d[i];
		double vi = (h[i] + 500.0*Ce*di*(dn-di) - (hts*(dn-di)+hrs*di)/dn) * sqrt( 0.002*dn/(ITURP_2001_6::Wavelength(f)*di*(dn-di)) );
		if( vi > vmax )
		{
			vmax = vi;
			dindex = i;
		}
	}
	return dindex;
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 5.1.3
// hrs:             receive antenna height above mean sea level (m)
// n:               number of profile elements
// d:               distance from transmitter profile of n elements (km)
// h:               terrain height profile of n elements (m above mean sea level)
// ae:              median effective Earth radius (km)
// [out] theta_max: physical horizon elevation angle as seen by the receiving antenna (relative to the local horizontal) (mrad)
//                  i.e. maximum elevation angle from receiving antenna to terrain elements
// [out] dindex:    index of distance to transmitter profile d for which theta_max was found.
void ITURP_452_18::_MaxRxToTerrainElevationAngle(double hrs, unsigned int n, const double* d, const double* h,
                                                 double ae, double& theta_max, unsigned int& dindex)
{
double dn = d[n-1];

	theta_max = std::numeric_limits<double>::lowest();
	dindex = 0;
	for(unsigned int j=1 ; j<n-1 ; j++) // excludes transmit and receive locations
	{
		double theta_j = _ElevationAngle(hrs, h[j], dn-d[j], ae);
		if( theta_j > theta_max )
		{
			theta_max = theta_j;
			dindex = j;
		}
	}
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 5.1.6.2
// n:         number of profile elements
// d:         distance from transmitter profile of n elements (km)
// h:         terrain height profile of n elements (m above mean sea level)
// [out] hst: height of the smooth-Earth surface at the transmitting station location (m amsl)
// [out] hsr: height of the smooth-Earth surface at the receiving station location (m amsl)
void ITURP_452_18::_SmoothEarthHeights(unsigned int n, const double* d, const double* h, double& hst, double& hsr)
{
double v1=0, v2=0;
double dn = d[n-1];

	for(unsigned int i=1 ; i<n ; i++)
	{
		v1 += (d[i]-d[i-1])*(h[i]+h[i-1]);
		v2 += (d[i]-d[i-1])*(h[i]*(2.0*d[i]+d[i-1])+h[i-1]*(d[i]+2.0*d[i-1]));
	}
	hst = (2.0*v1*dn-v2)/(dn*dn);
	hsr = (v2-v1*dn)/(dn*dn);
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 5.1.6.3
// hts:        transmit antenna height above mean sea level (m)
// hrs:        receive antenna height above mean sea level (m)
// n:          number of profile elements
// d:          distance from transmitter profile of n elements (km)
// h:          terrain height profile of n elements (m above mean sea level)
// hst:        height of the smooth-Earth surface at the transmitting station location (m amsl)
// hsr:        height of the smooth-Earth surface at the receiving station location (m amsl)
// [out] hstd: modified hst for the diffraction model (m amsl)
// [out] hsrd: modified hsr for the diffraction model (m amsl)
void ITURP_452_18::_SmoothEarthHeightsForDiffractionModel(double hts, double hrs, unsigned int n, const double* d, const double* h,
                                                          double hst, double hsr, double& hstd, double& hsrd)
{
double htc = hts;
double hrc = hrs;
double hobs = std::numeric_limits<double>::lowest();
double aobt = std::numeric_limits<double>::lowest();
double aobr = std::numeric_limits<double>::lowest();
double dn = d[n-1];
double h1 = h[0];
double hn = h[n-1];
double hstp, hsrp;

	for(unsigned int i=1 ; i<n-1 ; i++)
	{
		double Hi = h[i] - (htc*(dn-d[i])+hrc*d[i])/dn;
		double aobti = Hi/d[i];
		double aobri = Hi/(dn-d[i]);
		hobs = std::max(hobs, Hi);
		aobt = std::max(aobt, aobti);
		aobr = std::max(aobr, aobri);
	}

	if( hobs <= 0)
	{
		hstp = hst;
		hsrp = hsr;
	}
	else
	{
		double gt = aobt/(aobt+aobr);
		double gr = aobr/(aobt+aobr);
		hstp = hst-hobs*gt;
		hsrp = hsr-hobs*gr;
	}

	if( hstp > h1 )
		hstd = h1;
	else
		hstd = hstp;

	if( hsrp > hn)
		hsrd = hn;
	else
		hsrd = hsrp;
}

// ITU-R P.452-18, Attachment 2 to Annex 1, Section 5.1.6.4
// htg:       transmit antenna centre height above ground level (m)
// hrg:       receive antenna centre height above ground level (m)
// n:         number of profile elements
// d:         distance from transmitter profile of n elements (km)
// h:         terrain height profile of n elements (m above mean sea level)
// hst:       height of the smooth-Earth surface at the transmitting station location (m amsl)
// hsr:       height of the smooth-Earth surface at the receiving station location (m amsl)
// ilt:       index of the profile point at distance dlt from the transmitter
// ilr:       index of the profile point at distance dlr from the receiver
// [out] hte: effective height of the transmitting antenna for the ducting/layer-reflection model (m)
// [out] hre: effective height of the receiving antenna for the ducting/layer-reflection model (m)
// [out] hm:  terrain roughness (i.e. maximum height of the terrain above the smooth-Earth
//            surface in the section of the path between, and including, the horizon points) (m)
void ITURP_452_18::_EffectiveHeightsAndTerrainRoughness(double htg, double hrg, unsigned int n, const double* d, const double* h,
                                                        double hst, double hsr, unsigned int ilt, unsigned int ilr, 
                                                        double& hte, double& hre, double& hm)
{
double h1 = h[0];
double hn = h[n-1];
double dn = d[n-1];
double m;

	hst = std::min(hst, h1);
	hsr = std::min(hsr, hn);
	m = (hsr-hst)/dn;
	hte = htg + h1 - hst;
	hre = hrg + hn - hsr;
	hm = std::numeric_limits<double>::lowest();
	for(unsigned int i=ilt ; i<=ilr ; i++)
	{
		double hmi = h[i] - (hst + m*d[i]);
		hm = std::max(hm, hmi);
	}
}

// ITU-R P.452-18, Attachment 3 to Annex 1
// [return]: an approximation to the inverse complementary cumulative normal distribution function
double ITURP_452_18::_I(double x)
{
constexpr double C0 = 2.515516698;
constexpr double C1 = 0.802853;
constexpr double C2 = 0.010328;
constexpr double D1 = 1.432788;
constexpr double D2 = 0.189269;
constexpr double D3 = 0.001308;

	x = std::max(x, 0.000001);
	x = std::min(x, 0.999999);

	auto T = [] (double a) -> double
	{
		return sqrt(-2.0*log(a));
	};

	auto Xi = [T] (double b) -> double
	{
	double Tx = T(b);

		return (((C2*Tx+C1)*Tx)+C0) / (((D3*Tx+D2)*Tx+D1)*Tx+1);
	};

	if( x <= 0.5)
		return T(x)-Xi(x);
	else
		return Xi(1.0-x) - T(1.0-x);
}

bool ITURP_452_18::_IsAUTO(double param)
{
	return std::isnan(param);
}