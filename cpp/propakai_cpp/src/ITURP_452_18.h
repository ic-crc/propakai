/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once
#include <limits>
#include <vector>
#include <cstddef>
#include "DigitalMap.h"


class ITURP_452_18
{
public:
	static constexpr double AUTO = std::numeric_limits<double>::quiet_NaN();

	enum RadioClimaticZone : int
	{
		COASTAL_LAND = 3,
		INLAND       = 4,
		SEA          = 1
	};

	enum ClutterCategory : int
	{
		WATER_SEA           = 1,
		OPEN_RURAL          = 2,
		SUBURBAN            = 3,
		URBAN_TREES_FOREST  = 4,
		DENSE_URBAN         = 5
	};

	/**
	 * @brief The basic transmission loss (dB) not exceeded for the required annual percentage time p%.
	 *
	 * @param f_GHz      Frequency (GHz), with 0.1 <= f_GHz <= 50.0.
	 * @param p_percent  Required time percentage for which the calculated basic transmission
	 *                   loss is not exceeded (%), with 0.001 <= p_percent <= 50.0.
	 * @param worstMonth Use true to indicate an average "worst month" prediction, false to
	 *                   indicate an average annual prediction.
	 * @param latt       Latitude of transmitter (interfering station) (degrees),
	 *                   with -90 <= latt <= 90.
	 * @param lont       Longitude of transmitter (interfering station) (degrees),
	 *                   with -180 <= lont <= 180.
	 * @param latr       Latitude of receiver (interfered-with station) (degrees),
	 *                   with -90 <= latr <= 90.
	 * @param lonr       Longitude of receiver (interfered-with station) (degrees),
	 *                   with -180 <= lonr <= 180.
	 * @param htg_m      Transmitter's (interfering station's) antenna centre height above ground
	 *                   level (m).
	 * @param hrg_m      Receiver's (interfered-with station's) antenna centre height above ground
	 *                   level (m).
	 * @param Gt_dBi     Transmitter's (interfering station's) antenna gain in the direction of the
	 *                   horizon along the great-circle interference path (dBi).
	 * @param Gr_dBi     Receiver's (interfered-with station's) antenna gain in the direction of the
	 *                   horizon along the great-circle interference path (dBi).
	 * @param vpol       true to indicate vertical polarization, false to indicate horizontal
	 *                   polarization.
	 * @param n          Number of points in the profiles, with 3 <= n.
	 * @param d_km       Distance from transmitter (interfering station) profile of n points (km).
	 * @param h_mamsl    Terrain height profile of n points (m above mean sea level).
	 * @param cc         (Optional) Clutter category profile of n points (1=Water/Sea,
	 *                   2=Open/Rural, 3=Suburban, 4=Urban/Trees/Forest, 5=Dense Urban).
	 *                   cc is ignored when rch is specified, otherwise Open/Rural is assumed
	 *                   everywhere when cc is set to nullptr.
	 * @param rch_m      (Optional) Representative clutter height (m) profile of n points.
	 * @param rcz        (Optional) Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
	 *                   4=Inland). Inland is assumed everywhere when rcz is set to nullptr.
	 * @param dct_km     (Optional) Distance of the transmitter from the coast (km), in the
	 *                   direction of the other terminal. For a terminal on a ship or sea platform
	 *                   the distance is zero. When set to AUTO, dct_km is automatically estimated
	 *                   using the radio climate zone (rcz) and distance (d_km) profiles.
	 * @param dcr_km     (Optional) Distance of the receiver from the coast (km), in the
	 *                   direction of the other terminal. For a terminal on a ship or sea platform
	 *                   the distance is zero. When set to AUTO, dcr_km is automatically estimated
	 *                   using the radio climate zone (rcz) and distance (d_km) profiles.
	 * @param P_hPa      (Optional) Atmospheric pressure (hPa). Default is 1013.25 hPa.
	 * @param T_C        (Optional) Temperature (°C). Default is 15°C.
	 * @param deltaN     (Optional) Average radio-refractivity lapse-rate through the lowest 1 km
	 *                   of the atmosphere (N-units/km). When set to AUTO, deltaN is automatically
	 *                   obtained using one of the recommendation's digital maps at mid-distance
	 *                   between latt/lont and latr/lonr.
	 * @param N0         (Optional) Sea-level surface refractivity (N-units). When set to AUTO,
	 *                   N0 is automatically obtained using one of the recommendation's digital
	 *                   maps at mid-distance between latt/lont and latr/lonr.
	 *
	 * @return The basic transmission loss (dB) not exceeded for the required annual percentage
	 *         time p%.
	 */
	static double ClearAirBasicTransmissionLoss(double f_GHz, double p_percent, bool worstMonth, double latt, double lont, double latr, double lonr,
												double htg_m, double hrg_m, double Gt_dBi, double Gr_dBi, bool vpol, unsigned int n, const double* d_km,
												const double* h_mamsl, const ClutterCategory* cc=nullptr, const double* rch_m=nullptr, const RadioClimaticZone* rcz=nullptr,
												double dct_km=AUTO, double dcr_km=AUTO, double P_hPa=1013.25, double T_C=15.0, double deltaN=AUTO, double N0=AUTO);

protected:
	static const DigitalMap s_DN50_map;
	static const DigitalMap s_N050_map;

	static void LengthOfPathSectionsProfile(unsigned int n, const double* d, std::vector<double>& lopsVector);
	static double Dct(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static double Dcr(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static void EffectiveEarthRadius(double deltaN, double& ae, double& aB);
	static double AnnualEquivalentTimePercent(double pw, double lat, double omega);
	static double B0Calc(double lat, double dtm, double dlm);
	static void LongestContinuousLand(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops, double &dtm, double& dlm);
	static double OverWaterPercent(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static double TotalGaseousAbsorption(double f, double hts, double hrs, double dn, double rho, double P, double TK);
	static void LoSPropagationLoss(double f, double p, double B0, double hts, double hrs, double dn, double dlt, double dlr, double omega, double P, double TK, double& Lbfsg, double& Lb0p, double& Lb0B);
	static double BullingtonDiffractionLoss(double f, double htc, double hrc, double Ce, unsigned int n, const double* d, const double* g);
	static double SphericalEarthDiffractionLoss(double f, bool vpol, double dn, double ap, double omega, double htesph, double hresph);
	static double FirstTermSphericalEarthDiffractionLoss(double f, bool vpol, double dn, double adft, double omega, double htesph, double hresph);
	static double FirstTermSubCalculation(double f, bool vpol, double dn, double adft, double perm, double conduct, double htesph, double hresph);
	static void GProfile(unsigned int n, const double* d, const double* h, const ClutterCategory* cc, const double* rch, std::vector<double>& gVector);
	static double ReprHeight(ClutterCategory cc);
	static double DeltaBullingtonDiffractionLoss(double f, double htc, double hrc, bool vpol, double ap, double Ce, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd);
	static void DiffractionLoss(double f, double p, double B0, double htc, double hrc, bool vpol, double ae, double aB, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd, double Lbfs, double Lb0p, double& Ldp, double& Lbd50, double& Lbd);
	static double TroposcatterLoss(double f, double p, double Gt, double Gr, double dn, double theta, double N0, double P, double TK);
	static double DuctingLayerReflectionLoss(double f, double p, double ae, double B0, double dlm, double dn, double hts, double hrs, double dlt, double dlr, double thetat, double thetar, double hte, double hre, double hm, double omega, double dct, double dcr, double P, double TK);
	static double OverallPrediction(double p, double B0, double dn, double omega, double htc, double hrc, double ae, unsigned int n, const double* d, const double* h, double Lb0p, double Lb0B, double Ldp, double Lbd50, double Lba, double Lbd, double Lbs);
	static void PathProfileParameters(double f, double htg, double hrg, unsigned int n, const double* d, const double* h, double ae, double& dlt, double& dlr, double& thetat, double& thetar, double& theta, double& hstd, double& hsrd, double& hte, double& hre, double& hm);
	static double ElevationAngle(double hamsl_from, double hamsl_to, double distKm, double ae);
	static void MaxTxToTerrainElevationAngle(double hts, unsigned int n, const double* d, const double* h, double ae, double& theta_max, unsigned int& dindex);
	static unsigned int LoSMaxDiffractionDist(double f, double hts, double hrs, unsigned int n, const double* d, const double* h, double Ce);
	static void MaxRxToTerrainElevationAngle(double hrs, unsigned int n, const double* d, const double* h, double ae, double& theta_max, unsigned int& dindex);
	static void SmoothEarthHeights(unsigned int n, const double* d, const double* h, double& hst, double& hsr);
	static void SmoothEarthHeightsForDiffractionModel(double hts, double hrs, unsigned int n, const double* d, const double* h, double hst, double hsr, double& hstd, double& hsrd);
	static void EffectiveHeightsAndTerrainRoughness(double htg, double hrg, unsigned int n, const double* d, const double* h, double hst, double hsr, unsigned int ilt, unsigned int ilr, double& hte, double& hre, double& hm);
	static double I(double x);
	static bool IsAUTO(double param);

private:
	// Prevent instantiation
	ITURP_452_18() = delete;
	ITURP_452_18(const ITURP_452_18&) = delete;
	ITURP_452_18(ITURP_452_18&&) = delete;
	ITURP_452_18& operator=(const ITURP_452_18&) = delete;
	ITURP_452_18& operator=(ITURP_452_18&&) = delete;
};
