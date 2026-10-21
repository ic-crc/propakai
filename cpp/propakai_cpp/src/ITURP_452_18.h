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


class ITURP_452_18
{
public:
	inline static constexpr double AUTO = std::numeric_limits<double>::quiet_NaN();

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

	static bool Init_DN50(const char* pathname);
	static bool Init_N050(const char* pathname);

	static double ClearAirBasicTransmissionLoss(double f, double p, bool worstMonth, double latt, double lont, double latr, double lonr,
	                                            double htg, double hrg, double Gt, double Gr, bool vpol, unsigned int n, const double* d, const double* h,
	                                            const ClutterCategory* cc=nullptr, const double* rch=nullptr, const RadioClimaticZone* rcz=nullptr,
	                                            double dct=AUTO, double dcr=AUTO, double P=1013.25, double TC=15, double deltaN=AUTO, double N0=AUTO);

protected:
	static constexpr int _DN50_SIZE = 29161;
	static std::vector<double> _DN50_Vect;
	static constexpr int _N050_SIZE = 29161;
	static std::vector<double> _N050_Vect;

	static double _DN50(double lat, double lon);
	static double _N050(double lat, double lon);
	static void _LengthOfPathSectionsProfile(unsigned int n, const double* d, std::vector<double>& lopsVector);
	static double _Dct(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static double _Dcr(unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static void _EffectiveEarthRadius(double deltaN, double& ae, double& aB);
	static double _AnnualEquivalentTimePercent(double pw, double lat, double omega);
	static double _B0(double lat, double dtm, double dlm);
	static void _LongestContinuousLand(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops, double &dtm, double& dlm);
	static double _OverWaterPercent(double dn, unsigned int n, const RadioClimaticZone* rcz, const double* lops);
	static double _TotalGaseousAbsorption(double f, double hts, double hrs, double dn, double rho, double P, double TK);
	static void _LoSPropagationLoss(double f, double p, double B0, double hts, double hrs, double dn, double dlt, double dlr, double omega, double P, double TK, double& Lbfsg, double& Lb0p, double& Lb0B);
	static double _BullingtonDiffractionLoss(double f, double htc, double hrc, double Ce, unsigned int n, const double* d, const double* g);
	static double _SphericalEarthDiffractionLoss(double f, bool vpol, double dn, double ap, double omega, double htesph, double hresph);
	static double _FirstTermSphericalEarthDiffractionLoss(double f, bool vpol, double dn, double adft, double omega, double htesph, double hresph);
	static double _FirstTermSubCalculation(double f, bool vpol, double dn, double adft, double perm, double conduct, double htesph, double hresph);
	static void _gProfile(unsigned int n, const double* d, const double* h, const ClutterCategory* cc, const double* rch, std::vector<double>& gVector);
	static double _reprHeight(ClutterCategory cc);
	static double _DeltaBullingtonDiffractionLoss(double f, double htc, double hrc, bool vpol, double ap, double Ce, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd);
	static void _DiffractionLoss(double f, double p, double B0, double htc, double hrc, bool vpol, double ae, double aB, unsigned int n, const double* d, const double* g, double omega, double hstd, double hsrd, double Lbfs, double Lb0p, double& Ldp, double& Lbd50, double& Lbd);
	static double _TroposcatterLoss(double f, double p, double Gt, double Gr, double dn, double theta, double N0, double P, double TK);
	static double _DuctingLayerReflectionLoss(double f, double p, double ae, double B0, double dlm, double dn, double hts, double hrs, double dlt, double dlr, double thetat, double thetar, double hte, double hre, double hm, double omega, double dct, double dcr, double P, double TK);
	static double _OverallPrediction(double p, double B0, double dn, double omega, double htc, double hrc, double ae, unsigned int n, const double* d, const double* h, double Lb0p, double Lb0B, double Ldp, double Lbd50, double Lba, double Lbd, double Lbs);
	static void _PathProfileParameters(double f, double htg, double hrg, unsigned int n, const double* d, const double* h, double ae, double& dlt, double& dlr, double& thetat, double& thetar, double& theta, double& hstd, double& hsrd, double& hte, double& hre, double& hm);
	static double _ElevationAngle(double hamsl_from, double hamsl_to, double distKm, double ae);
	static void _MaxTxToTerrainElevationAngle(double hts, unsigned int n, const double* d, const double* h, double ae, double& theta_max, unsigned int& dindex);
	static unsigned int _LoSMaxDiffractionDist(double f, double hts, double hrs, unsigned int n, const double* d, const double* h, double Ce);
	static void _MaxRxToTerrainElevationAngle(double hrs, unsigned int n, const double* d, const double* h, double ae, double& theta_max, unsigned int& dindex);
	static void _SmoothEarthHeights(unsigned int n, const double* d, const double* h, double& hst, double& hsr);
	static void _SmoothEarthHeightsForDiffractionModel(double hts, double hrs, unsigned int n, const double* d, const double* h, double hst, double hsr, double& hstd, double& hsrd);
	static void _EffectiveHeightsAndTerrainRoughness(double htg, double hrg, unsigned int n, const double* d, const double* h, double hst, double hsr, unsigned int ilt, unsigned int ilr, double& hte, double& hre, double& hm);
	static double _I(double x);
	static bool _IsAUTO(double param);

private:
	// Prevent instantiation
	ITURP_452_18() = delete;                                 // Delete default constructor
	ITURP_452_18(const ITURP_452_18&) = delete;              // Delete copy constructor
	ITURP_452_18(ITURP_452_18&&) = delete;                   // Delete move constructor
	ITURP_452_18& operator=(const ITURP_452_18&) = delete;   // Delete copy assignment
	ITURP_452_18& operator=(ITURP_452_18&&) = delete;        // Delete move assignment
};