/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_838_3.h"
#include <cmath>


// 'static' here means "private to this .cpp file only"
static constexpr double radians(double deg)
{
	return deg * (3.14159265358979323846 / 180.0);
}

double ITURP_838_3::RainAttenuation(double f_GHz, double R_mmhr, double theta_degrees, double tau_degrees)
{
	const Coeffs coeffs = Coefficients(f_GHz, theta_degrees, tau_degrees);
	const double gamma_R = coeffs.k*pow(R_mmhr, coeffs.alpha);
	return gamma_R;
}

ITURP_838_3::Coeffs ITURP_838_3::Coefficients(double f_GHz, double theta_degrees, double tau_degrees)
{
	const double theta_rad = radians(theta_degrees);
	const double tau_rad = radians(tau_degrees);
	const double kH = KH(f_GHz);
	const double kV = KV(f_GHz);
	const double aH = AH(f_GHz);
	const double aV = AV(f_GHz);
	const double cos_th = cos(theta_rad);
	const double cos_2tau = cos(2*tau_rad);
	const double k = (kH+kV+((kH-kV)*cos_th*cos_th*cos_2tau))/2.0;
	const double alpha = ((kH*aH)+(kV*aV)+(((kH*aH)-(kV*aV))*cos_th*cos_th*cos_2tau))/(2.0*k);
	return {k, alpha};
}

double ITURP_838_3::KH(double f_GHz)
{
	static constexpr std::array<double, 4> A = {-5.33980, -0.35351, -0.23789, -0.94158};
	static constexpr std::array<double, 4> B = {-0.10008, 1.26970, 0.86036, 0.64552};
	static constexpr std::array<double, 4> C = {1.13098, 0.45400, 0.15354, 0.16817};
	constexpr double MK = -0.18961;
	constexpr double CK = 0.71147;
	return PolK(f_GHz, A, B, C, MK, CK);
}

double ITURP_838_3::KV(double f_GHz)
{
	static constexpr std::array<double, 4> A = {-3.80595, -3.44965, -0.39902, 0.50167};
	static constexpr std::array<double, 4> B = {0.56934, -0.22911, 0.73042, 1.07319};
	static constexpr std::array<double, 4> C = {0.81061, 0.51059, 0.11899, 0.27195};
	constexpr double MK = -0.16398;
	constexpr double CK = 0.63297;
	return PolK(f_GHz, A, B, C, MK, CK);
}

double ITURP_838_3::AH(double f_GHz)
{
	static constexpr std::array<double, 5> A = {-0.14318, 0.29591, 0.32177, -5.37610, 16.1721};
	static constexpr std::array<double, 5> B = {1.82442, 0.77564, 0.63773, -0.96230, -3.29980};
	static constexpr std::array<double, 5> C = {-0.55187, 0.19822, 0.13164, 1.47828, 3.43990};
	constexpr double MA = 0.67849;
	constexpr double CA = -1.95537;
	return PolAlpha(f_GHz, A, B, C, MA, CA);
}

double ITURP_838_3::AV(double f_GHz)
{
	static constexpr std::array<double, 5> A = {-0.07771, 0.56727, -0.20238, -48.2991, 48.5833};
	static constexpr std::array<double, 5> B = {2.33840, 0.95545, 1.14520, 0.791669, 0.791459};
	static constexpr std::array<double, 5> C = {-0.76284, 0.54039, 0.26809, 0.116226, 0.116479};
	constexpr double MA = -0.053739;
	constexpr double CA = 0.83433;
	return PolAlpha(f_GHz, A, B, C, MA, CA);
}

double ITURP_838_3::PolK(double f_GHz, const std::array<double, 4>& a, const std::array<double, 4>& b, const std::array<double, 4>& c, double mk, double ck)
{
	const double log10_f = std::log10(f_GHz);
	double sum = 0.0;

	for (std::size_t j=0 ; j<4 ; ++j)
	{
		const double base = (log10_f - b[j]) / c[j];
		sum += a[j] * std::exp(-(base * base));
	}

	const double log10_k = sum + (mk * log10_f) + ck;
	return std::pow(10.0, log10_k);
}

double ITURP_838_3::PolAlpha(double f_GHz, const std::array<double, 5>& a, const std::array<double, 5>& b, const std::array<double, 5>& c, double ma, double ca)
{
	const double log10_f = std::log10(f_GHz);
	double sum = 0.0;

	for (std::size_t j=0 ; j<5 ; ++j)
	{
		const double base = (log10_f - b[j]) / c[j];
		sum += a[j] * std::exp(-(base * base));
	}

	const double alpha = sum + (ma * log10_f) + ca;
	return alpha;
}
