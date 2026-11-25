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


class ITURP_1812_8
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
	 * @brief The basic transmission loss not exceeded for p% time and pL% locations.
	 *
	 * @param f_GHz      Frequency (GHz), with 0.03 <= f_GHz <= 6.0.
	 * @param p_percent  Percentage of average year for which the calculated basic transmission
	 *                   loss is not exceeded (%), with 1.0 <= p_percent <= 50.0.
	 * @param pL_percent Percentage of locations for which the calculated basic transmission
	 *                   loss is not exceeded (%), with 1.0 <= pL_percent <= 99.0.
	 * @param latt       Latitude of transmitter (degrees), with -80 <= latt <= 80.
	 * @param lont       Longitude of transmitter (degrees), with -180 <= lont <= 180.
	 * @param latr       Latitude of receiver (degrees), with -80 <= latr <= 80.
	 * @param lonr       Longitude of receiver (degrees), with -180 <= lonr <= 180.
	 * @param htg_m      Transmit antenna centre height above ground level (m), with 1 <= htg_m <= 3000.
	 * @param hrg_m      Receive antenna centre height above ground level (m), with 1 <= hrg <= 3000.
	 * @param vpol       true to indicate vertical polarization, false to indicate horizontal
	 *                   polarization.
	 * @param n          Number of points in the profiles, with 3 <= n.
	 * @param d_km       Distance from transmitter profile of n points (km).
	 * @param h_mamsl    Terrain height profile of n points (m above mean sea level).
	 * @param cc        (Optional) Clutter category profile of n points (1=Water/Sea,
	 *                  2=Open/Rural, 3=Suburban, 4=Urban/Trees/Forest, 5=Dense Urban).
	 *                  cc is ignored when either rch_m or sh_mamsl is specified, otherwise Open/Rural
	 *                  is assumed everywhere when cc is set to nullptr.
	 * @param rch_m     (Optional) Representative clutter height (m) profile of n points.
	 *                  rch_m is ignored if sh_mamsl is specified.
	 * @param sh_mamsl  (Optional) Surface height (m above mean sea level) profile of n points.
	 * @param rcz       (Optional) Radio climatic zone profile of n points (1=Sea, 3=Coastal Land,
	 *                  4=Inland). Inland is assumed everywhere when rcz is set to nullptr.
	 * @param dct_km    (Optional) Distance of the transmitter from the coast (km), in the
	 *                  direction of the other terminal. For a terminal on a ship or sea platform
	 *                  the distance is zero. When set to AUTO, dct_km is automatically estimated
	 *                  using the radio climate zone (rcz) and distance (d_km) profiles.
	 * @param dcr_km    (Optional) Distance of the receiver from the coast (km), in the
	 *                  direction of the other terminal. For a terminal on a ship or sea platform
	 *                  the distance is zero. When set to AUTO, dcr_km is automatically estimated
	 *                  using the radio climate zone (rcz) and distance (d_km) profiles.
	 * @param deltaN    (Optional) Average radio-refractivity lapse-rate through the lowest 1 km
	 *                  of the atmosphere (N-units/km). When set to AUTO, deltaN is automatically
	 *                  obtained using one of the recommendation's digital maps at mid-distance
	 *                  between latt/lont and latr/lonr.
	 * @param N0        (Optional) Sea-level surface refractivity (N-units). When set to AUTO,
	 *                  N0 is automatically obtained using one of the recommendation's digital
	 *                  maps at mid-distance between latt/lont and latr/lonr.
	 * @param wa_m      (Optional) Prediction resolution (m), the width of the square area over
	 *                  which the location variability applies. Default value is 100 m.
	 *
	 * @return The basic transmission loss (dB) not exceeded for p% time and pL% locations.
	 */
	static double BasicTransmissionloss(double f_GHz, double p_percent, double pL_percent, double latt, double lont, double latr, double lonr,
										double htg_m, double hrg_m, bool vpol, unsigned int n, const double* d_km, const double* h_mamsl,
										const ClutterCategory* cc=nullptr, const double* rch_m=nullptr, const double* sh_mamsl=nullptr,
										const RadioClimaticZone* rcz=nullptr, double dct_km=AUTO, double dcr_km=AUTO, double deltaN=AUTO,
										double N0=AUTO, double wa_m=100.0);


	/**
	 * @brief The field strength exceeded for p% time and pL% locations.
	 *
	 * @param f_GHz Frequency (GHz), with 0.03 <= f_GHz <= 6.0.
	 * @param Lb_dB Basic transmission loss (dB), obtained from the BasicTransmissionloss()
	 *              function.
	 *
	 * @return The field strength normalized to 1 kW effective radiated power exceeded for
	 *         p% time and pL% locations (dBuV/m).
	 */
	static double FieldStrength(double f_GHz, double Lb_dB);

protected:
	static const DigitalMap s_DN50_map;
	static const DigitalMap s_N050_map;

	static void LengthOfPathSectionsProfile(unsigned int n, const double* d, std::vector<double>& lopsVector);
	static double Dct(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static double Dcr(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static void GProfile(unsigned int n, const double* h, const ClutterCategory* cc, const double* rch, const double* sh, std::vector<double>& gVector, double& R);
	static double ReprHeight(ClutterCategory cc);
	static void LongestContinuousLand(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops, double &dtm, double& dlm);
	static double B0Calc(double lat, double dtm, double dlm);
	static void EffectiveEarthRadius(double deltaN, double& ae, double& aB);
	static double OverWaterPercent(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static void LoSPropagationLoss(double f, double p, double B0, double hts, double hrs, double dn, double dlt, double dlr, double& Lbfs, double& Lb0p, double& Lb0B);
	static double BullingtonDiffractionLoss(double f, double htc, double hrc, double Ce, unsigned int n, const double* d, const double* g);
	static double SphericalEarthDiffractionLoss(double f, bool vpol, double dn, double ap, double omega, double htesph, double hresph);
	static double FirstTermSphericalEarthDiffractionLoss(double f, bool vpol, double dn, double adft, double omega, double htesph, double hresph);
	static double FirstTermSubCalculation(double f, bool vpol, double dn, double adft, double perm, double conduct, double htesph, double hresph);
	static double DeltaBullingtonDiffractionLoss(double f, double htc, double hrc, bool vpol, double ap, double Ce, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd);
	static void DiffractionLoss(double f, double p, double B0, double htc, double hrc, bool vpol, double ae, double aB, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd, double Lbfs, double Lb0p, double& Ldp, double& Lbd50, double& Lbd);
	static double TroposcatterLoss(double f, double p, double dn, double theta, double N0);
	static double DuctingLayerReflectionLoss(double f, double p, double ae, double B0, double dlm, double dn, double hts, double hrs, double dlt, double dlr, double thetat, double thetar, double hte, double hre, double hm, double omega, double dct, double dcr);
	static double Loc50BasicTransmissionLoss(double p, double B0, double dn, double theta, double omega, double Lb0p, double Lb0B, double Ldp, double Lbd50, double Lba, double Lbd, double Lbs);
	static double BasicTransmissionLoss(double f, double wa, double pL, double hrg, double R, double Lb0p, double Lbc);
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
	ITURP_1812_8() = delete;
	ITURP_1812_8(const ITURP_1812_8&) = delete;
	ITURP_1812_8(ITURP_1812_8&&) = delete;
	ITURP_1812_8& operator=(const ITURP_1812_8&) = delete;
	ITURP_1812_8& operator=(ITURP_1812_8&&) = delete;
};
