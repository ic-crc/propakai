/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_2145_0.h"
#include <cmath>
#include <stdexcept>
#include <algorithm>
#include "ITURP_1511_3.h"


const std::vector<ITURP_2145_0::NominalProb> ITURP_2145_0::s_ANNUAL_NOMINAL_PROBS = {
	{0.01, "001"}, {0.02, "002"}, {0.03, "003"}, {0.05, "005"},
	{0.1, "01"}, {0.2, "02"}, {0.3, "03"}, {0.5, "05"},
	{1, "1"}, {2, "2"}, {3, "3"}, {5, "5"}, {10, "10"}, {20, "20"}, {30, "30"}, {50, "50"},
	{60, "60"}, {70, "70"}, {80, "80"}, {90, "90"}, {95, "95"}, {99, "99"}
};

const std::vector<ITURP_2145_0::NominalProb> ITURP_2145_0::s_MONTHLY_NOMINAL_PROBS = {
	{0.1, "01"}, {0.2, "02"}, {0.3, "03"}, {0.5, "05"},
	{1, "1"}, {2, "2"}, {3, "3"}, {5, "5"}, {10, "10"}, {20, "20"}, {30, "30"}, {50, "50"},
	{60, "60"}, {70, "70"}, {80, "80"}, {90, "90"}, {95, "95"}, {99, "99"}
};

const std::array<std::string, 12> ITURP_2145_0::s_MONTH_FOLDERS = {
	"_Month01/", "_Month02/", "_Month03/", "_Month04/", "_Month05/", "_Month06/", "_Month07/",
	"_Month08/", "_Month09/", "_Month10/", "_Month11/", "_Month12/"
};

const std::array<std::string, 4> ITURP_2145_0::s_PARAMS = {
	"P", "RHO", "T", "V"
};

DigitalMap make_p2145_0_map(const std::string& filename)
{
	return { filename, -90.0, +0.25, 721, -180.0, +0.25, 1441, InterpolationType::Bilinear };
}

const std::unordered_map<std::string, DigitalMap> ITURP_2145_0::s_Annual_maps = []()
{
	std::unordered_map<std::string, DigitalMap> annual_maps;

	std::string path;
	for (const std::string& param : s_PARAMS)
	{
		for (const NominalProb& nomProb : s_ANNUAL_NOMINAL_PROBS)
		{
			path = "p2145_0/" + param + "_Annual/" + param + "_" + nomProb.pStr + ".TXT";
			annual_maps.emplace(path, make_p2145_0_map(path));
		}

		path = "p2145_0/" + param + "_Annual/" + param + "_mean.TXT";
		annual_maps.emplace(path, make_p2145_0_map(path));

		path = "p2145_0/" + param + "_Annual/" + param + "_std.TXT";
		annual_maps.emplace(path, make_p2145_0_map(path));

		if (param == "RHO")
			path = "p2145_0/" + param + "_Annual/VSCH.TXT";
		else
			path = "p2145_0/" + param + "_Annual/" + param + "SCH.TXT";
		annual_maps.emplace(path, make_p2145_0_map(path));

		path = "p2145_0/" + param + "_Annual/Z_ground.TXT";
		annual_maps.emplace(path, make_p2145_0_map(path));
	}

	path = "p2145_0/Weibull_Annual/kV.TXT";
	annual_maps.emplace(path, make_p2145_0_map(path));

	path = "p2145_0/Weibull_Annual/lambdaV.TXT";
	annual_maps.emplace(path, make_p2145_0_map(path));

	path = "p2145_0/Weibull_Annual/VSCH.TXT";
	annual_maps.emplace(path, make_p2145_0_map(path));

	path = "p2145_0/Weibull_Annual/Z_ground.TXT";
	annual_maps.emplace(path, make_p2145_0_map(path));

	return annual_maps;
}();

const std::unordered_map<std::string, DigitalMap> ITURP_2145_0::s_Monthly_maps = []()
{
	std::unordered_map<std::string, DigitalMap> monthly_maps;

	std::string path;
	for (const std::string& param : s_PARAMS)
	{
		for (const std::string& month : s_MONTH_FOLDERS)
		{
			for (const NominalProb& nomProb : s_ANNUAL_NOMINAL_PROBS)
			{
				path = "p2145_0/" + param + month + param + "_" + nomProb.pStr + ".TXT";
				monthly_maps.emplace(path, make_p2145_0_map(path));
			}

			path = "p2145_0/" + param + month + param + "_mean.TXT";
			monthly_maps.emplace(path, make_p2145_0_map(path));

			path = "p2145_0/" + param + month + param + "_std.TXT";
			monthly_maps.emplace(path, make_p2145_0_map(path));

			if (param == "RHO")
				path = "p2145_0/" + param + month + "VSCH.TXT";
			else
				path = "p2145_0/" + param + month + param + "SCH.TXT";
			monthly_maps.emplace(path, make_p2145_0_map(path));

			path = "p2145_0/" + param + month + "Z_ground.TXT";
			monthly_maps.emplace(path, make_p2145_0_map(path));
		}
	}

	return monthly_maps;
}();

ITURP_2145_0::CCDFMaps ITURP_2145_0::GetCCDFMaps(double p_percent, int month, const std::string& param)
{
	std::string directory;
	const std::vector<NominalProb>* nomProbsPtr = nullptr;
	const std::unordered_map<std::string, DigitalMap>* mapsPtr = nullptr;
	if (month == -1)
	{
		nomProbsPtr =  &s_ANNUAL_NOMINAL_PROBS;
		mapsPtr = &s_Annual_maps;
		directory = "p2145_0/" + param + "_Annual/";
	}
	else if (month >= 1 && month <= 12)
	{
		nomProbsPtr =  &s_MONTHLY_NOMINAL_PROBS;
		mapsPtr = &s_Monthly_maps;
		directory = "p2145_0/" + param + s_MONTH_FOLDERS[static_cast<std::size_t>(month-1)];
	}
	else
		throw std::invalid_argument("Month must be between 1 and 12, or -1 for annual data.");
	const std::vector<NominalProb>& nomProbs = *nomProbsPtr;
	const std::unordered_map<std::string, DigitalMap>& maps = *mapsPtr;

	std::string path;
	for (size_t i=0; i<nomProbs.size()-1; ++i)
	{
		if (p_percent >= nomProbs[i].p && p_percent <= nomProbs[i+1].p)
		{
			const double below = nomProbs[i].p;
			const double above = nomProbs[i+1].p;

			path = directory + param + "_" + nomProbs[i].pStr + ".TXT";
			const DigitalMap& belowMap = maps.at(path);

			path = directory + param + "_" + nomProbs[i+1].pStr + ".TXT";
			const DigitalMap& aboveMap = maps.at(path);

			if (param == "RHO")
				path = directory + "VSCH.TXT";
			else
				path = directory + param + "SCH.TXT";
			const DigitalMap& schMap = maps.at(path);

			path = directory + "Z_ground.TXT";
			const DigitalMap& zMap = maps.at(path);

			return {below, belowMap, above, aboveMap, schMap, zMap};
		}
	}

	throw std::invalid_argument("p_percent is out of range.");
}

ITURP_2145_0::MeanStdDevMaps ITURP_2145_0::GetMeanStdDevMaps(int month, const std::string& param)
{
	std::string directory;
	const std::unordered_map<std::string, DigitalMap>* mapsPtr = nullptr;
	if (month == -1)
	{
		directory = "p2145_0/" + param + "_Annual/";
		mapsPtr = &s_Annual_maps;
	}
	else if (month >= 1 && month <= 12)
	{
		directory = "p2145_0/" + param + s_MONTH_FOLDERS[static_cast<std::size_t>(month-1)];
		mapsPtr = &s_Monthly_maps;
	}
	else
		throw std::invalid_argument("Month must be between 1 and 12, or -1 for annual data.");
	const std::unordered_map<std::string, DigitalMap>& maps = *mapsPtr;

	std::string path;

	path = directory + param + "_mean.TXT";
	const DigitalMap& meanMap = maps.at(path);

	path = directory + param + "_std.TXT";
	const DigitalMap& stdDevMap = maps.at(path);

	if (param == "RHO")
		path = directory + "VSCH.TXT";
	else
		path = directory + param + "SCH.TXT";
	const DigitalMap& schMap = maps.at(path);

	path = directory + "Z_ground.TXT";
	const DigitalMap& zMap = maps.at(path);

	return {meanMap, stdDevMap, schMap, zMap};
}

double ITURP_2145_0::CCDFInterpolation(double p_percent, double lat, double lon, double h_mamsl, const CCDFMaps& maps, ScalingFunc scalingFunc)
{
	if (!(std::abs(lat) <= 90.0 && std::abs(lon) <= 180.0))
		throw std::invalid_argument("lat must be in [-90, 90] and lon in [-180, 180].");

	// a)
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);
	const double alt = h_mamsl/1000.0; // convert from m to km

	double r = (90.0 + lat) / 0.25;
	double c = (180.0 + lon) / 0.25;
	constexpr std::size_t numRows = 721;
	constexpr std::size_t rowSize = 1441;
	constexpr double maxR = static_cast<double>(numRows-2);
	constexpr double maxC = static_cast<double>(rowSize-2);
	const std::size_t R = static_cast<std::size_t>(std::clamp(r, 0.0, maxR));
	const std::size_t C = static_cast<std::size_t>(std::clamp(c, 0.0, maxC));

	const std::size_t i0 = R*rowSize + C;
	const std::size_t i1 = (R+1)*rowSize + C;
	const std::size_t i2 = R*rowSize + (C+1);
	const std::size_t i3 = (R+1)*rowSize + (C+1);

	// c)
	const double Xpa0 = maps.pAboveMap.GetValueFromIndex(i0);
	const double Xpa1 = maps.pAboveMap.GetValueFromIndex(i1);
	const double Xpa2 = maps.pAboveMap.GetValueFromIndex(i2);
	const double Xpa3 = maps.pAboveMap.GetValueFromIndex(i3);
	const double Xpb0 = maps.pBelowMap.GetValueFromIndex(i0);
	const double Xpb1 = maps.pBelowMap.GetValueFromIndex(i1);
	const double Xpb2 = maps.pBelowMap.GetValueFromIndex(i2);
	const double Xpb3 = maps.pBelowMap.GetValueFromIndex(i3);

	// d)
	const double sch0 = maps.schMap.GetValueFromIndex(i0);
	const double sch1 = maps.schMap.GetValueFromIndex(i1);
	const double sch2 = maps.schMap.GetValueFromIndex(i2);
	const double sch3 = maps.schMap.GetValueFromIndex(i3);

	// e)
	const double alt0 = maps.zMap.GetValueFromIndex(i0);
	const double alt1 = maps.zMap.GetValueFromIndex(i1);
	const double alt2 = maps.zMap.GetValueFromIndex(i2);
	const double alt3 = maps.zMap.GetValueFromIndex(i3);

	// f)
	const double Xa0 = scalingFunc(Xpa0, sch0, alt, alt0);
	const double Xa1 = scalingFunc(Xpa1, sch1, alt, alt1);
	const double Xa2 = scalingFunc(Xpa2, sch2, alt, alt2);
	const double Xa3 = scalingFunc(Xpa3, sch3, alt, alt3);
	const double Xb0 = scalingFunc(Xpb0, sch0, alt, alt0);
	const double Xb1 = scalingFunc(Xpb1, sch1, alt, alt1);
	const double Xb2 = scalingFunc(Xpb2, sch2, alt, alt2);
	const double Xb3 = scalingFunc(Xpb3, sch3, alt, alt3);

	// g)
    const double Xabove = Xa0*((R+1-r)*(C+1-c)) + Xa1*((r-R)*(C+1-c)) + Xa2*((R+1-r)*(c-C)) + Xa3*((r-R)*(c-C));
    const double Xbelow = Xb0*((R+1-r)*(C+1-c)) + Xb1*((r-R)*(C+1-c)) + Xb2*((R+1-r)*(c-C)) + Xb3*((r-R)*(c-C));

	// h)
	const double X0 = Xbelow;
	const double X1 = Xabove;
	const double p0 = maps.pBelow;
	const double p1 = maps.pAbove;
	const double X = (X0*std::log10(p1/p_percent) + X1*std::log10(p_percent/p0)) / std::log10(p1/p0);

	return X;
}

double ITURP_2145_0::MeanStdDevInterpolation(double lat, double lon, double h_mamsl, const DigitalMap& mainMap,
                                             const DigitalMap& schMap, const DigitalMap& zMap, ScalingFunc scalingFunc)
{
	if (!(std::abs(lat) <= 90.0 && std::abs(lon) <= 180.0))
		throw std::invalid_argument("lat must be in [-90, 90] and lon in [-180, 180].");

	// a)
	if (std::isnan(h_mamsl))
		h_mamsl = ITURP_1511_3::TopographicHeight(lat, lon);
	const double alt = h_mamsl/1000.0; // convert from m to km

	double r = (90.0 + lat) / 0.25;
	double c = (180.0 + lon) / 0.25;
	constexpr std::size_t numRows = 721;
	constexpr std::size_t rowSize = 1441;
	constexpr double maxR = static_cast<double>(numRows-2);
	constexpr double maxC = static_cast<double>(rowSize-2);
	const std::size_t R = static_cast<std::size_t>(std::clamp(r, 0.0, maxR));
	const std::size_t C = static_cast<std::size_t>(std::clamp(c, 0.0, maxC));

	const std::size_t i0 = R*rowSize + C;
	const std::size_t i1 = (R+1)*rowSize + C;
	const std::size_t i2 = R*rowSize + (C+1);
	const std::size_t i3 = (R+1)*rowSize + (C+1);

	// b)
	const double Xp0 = mainMap.GetValueFromIndex(i0);
	const double Xp1 = mainMap.GetValueFromIndex(i1);
	const double Xp2 = mainMap.GetValueFromIndex(i2);
	const double Xp3 = mainMap.GetValueFromIndex(i3);

	// c)
	const double sch0 = schMap.GetValueFromIndex(i0);
	const double sch1 = schMap.GetValueFromIndex(i1);
	const double sch2 = schMap.GetValueFromIndex(i2);
	const double sch3 = schMap.GetValueFromIndex(i3);

	// d)
	const double alt0 = zMap.GetValueFromIndex(i0);
	const double alt1 = zMap.GetValueFromIndex(i1);
	const double alt2 = zMap.GetValueFromIndex(i2);
	const double alt3 = zMap.GetValueFromIndex(i3);

	// e)
	const double X0 = scalingFunc(Xp0, sch0, alt, alt0);
	const double X1 = scalingFunc(Xp1, sch1, alt, alt1);
	const double X2 = scalingFunc(Xp2, sch2, alt, alt2);
	const double X3 = scalingFunc(Xp3, sch3, alt, alt3);

    // f)
    const double X = X0*((R+1-r)*(C+1-c)) + X1*((r-R)*(C+1-c)) + X2*((R+1-r)*(c-C)) + X3*((r-R)*(c-C));
	
	return X;
}

double ITURP_2145_0::ExpScalingFunc(double xp, double sch, double alt, double alti)
{
	return xp*std::exp(-(alt-alti)/sch);
}

double ITURP_2145_0::AddScalingFunc(double xp, double sch, double alt, double alti)
{
	return xp+(sch*(alt-alti));
}

double ITURP_2145_0::DirectScalingFunc(double xp, double /*sch*/, double /*alt*/, double /*alti*/)
{
	return xp;
}

double ITURP_2145_0::SurfaceTotalPressure(double p_percent, double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	CCDFMaps maps = GetCCDFMaps(p_percent, month, "P");
	return CCDFInterpolation(p_percent, lat, lon, h_mamsl, maps, ExpScalingFunc);
}

double ITURP_2145_0::SurfaceTemperature(double p_percent, double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	CCDFMaps maps = GetCCDFMaps(p_percent, month, "T");
	return CCDFInterpolation(p_percent, lat, lon, h_mamsl, maps, AddScalingFunc);
}

double ITURP_2145_0::SurfaceWaterVapourDensity(double p_percent, double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	CCDFMaps maps = GetCCDFMaps(p_percent, month, "RHO");
	return CCDFInterpolation(p_percent, lat, lon, h_mamsl, maps, ExpScalingFunc);
}

double ITURP_2145_0::IntegratedWaterVapourContent(double p_percent, double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	CCDFMaps maps = GetCCDFMaps(p_percent, month, "V");
	return CCDFInterpolation(p_percent, lat, lon, h_mamsl, maps, ExpScalingFunc);
}

double ITURP_2145_0::MeanSurfaceTotalPressure(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "P");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.meanMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::MeanSurfaceTemperature(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "T");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.meanMap, maps.schMap, maps.zMap, AddScalingFunc);
}

double ITURP_2145_0::MeanSurfaceWaterVapourDensity(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "RHO");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.meanMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::MeanIntegratedWaterVapourContent(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "V");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.meanMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::StdDevSurfaceTotalPressure(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "P");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.stdDevMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::StdDevSurfaceTemperature(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "T");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.stdDevMap, maps.schMap, maps.zMap, DirectScalingFunc);
}

double ITURP_2145_0::StdDevSurfaceWaterVapourDensity(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "RHO");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.stdDevMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::StdDevIntegratedWaterVapourContent(double lat, double lon, int month /*= -1*/, double h_mamsl /*= AUTO*/)
{
	MeanStdDevMaps maps = GetMeanStdDevMaps(month, "V");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, maps.stdDevMap, maps.schMap, maps.zMap, ExpScalingFunc);
}

double ITURP_2145_0::WeibullShapeParameter(double lat, double lon, double h_mamsl /*= AUTO*/)
{
	const DigitalMap& kvMap = s_Annual_maps.at("p2145_0/Weibull_Annual/kV.TXT");
	const DigitalMap& schMap = s_Annual_maps.at("p2145_0/Weibull_Annual/VSCH.TXT");
	const DigitalMap& zMap = s_Annual_maps.at("p2145_0/Weibull_Annual/Z_ground.TXT");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, kvMap, schMap, zMap, DirectScalingFunc);
}

double ITURP_2145_0::WeibullScaleParameter(double lat, double lon, double h_mamsl /*= AUTO*/)
{
	const DigitalMap& lambdavMap = s_Annual_maps.at("p2145_0/Weibull_Annual/lambdaV.TXT");
	const DigitalMap& schMap = s_Annual_maps.at("p2145_0/Weibull_Annual/VSCH.TXT");
	const DigitalMap& zMap = s_Annual_maps.at("p2145_0/Weibull_Annual/Z_ground.TXT");
	return MeanStdDevInterpolation(lat, lon, h_mamsl, lambdavMap, schMap, zMap, ExpScalingFunc);
}
