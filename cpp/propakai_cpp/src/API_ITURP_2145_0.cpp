/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_ITURP_2145_0.h"
#include "ITURP_2145_0.h"


PROPAKAI_API double P2145_0_AUTO_CONSTANT()
{
	return ITURP_2145_0::AUTO;
}

PROPAKAI_API double P2145_0_SurfaceTotalPressure(double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::SurfaceTotalPressure(p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_SurfaceTemperature(double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::SurfaceTemperature(p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_SurfaceWaterVapourDensity(double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::SurfaceWaterVapourDensity(p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_IntegratedWaterVapourContent(double p_percent, double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::IntegratedWaterVapourContent(p_percent, lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_MeanSurfaceTotalPressure(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::MeanSurfaceTotalPressure(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_MeanSurfaceTemperature(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::MeanSurfaceTemperature(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_MeanSurfaceWaterVapourDensity(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::MeanSurfaceWaterVapourDensity(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_MeanIntegratedWaterVapourContent(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::MeanIntegratedWaterVapourContent(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_StdDevSurfaceTotalPressure(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::StdDevSurfaceTotalPressure(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_StdDevSurfaceTemperature(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::StdDevSurfaceTemperature(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_StdDevSurfaceWaterVapourDensity(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::StdDevSurfaceWaterVapourDensity(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_StdDevIntegratedWaterVapourContent(double lat, double lon, int month, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::StdDevIntegratedWaterVapourContent(lat, lon, month, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_WeibullShapeParameter(double lat, double lon, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::WeibullShapeParameter(lat, lon, h_mamsl);
	});
}

PROPAKAI_API double P2145_0_WeibullScaleParameter(double lat, double lon, double h_mamsl)
{
	return ExecuteSafely([&]() {
		return ITURP_2145_0::WeibullScaleParameter(lat, lon, h_mamsl);
	});
}
