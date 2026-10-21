/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "ITURP_2109_2.h"
#include "ITURP_1057_7.h"
#include <cmath>


// ITU-R P.2109-2, Annex 1, Section 3
// f_GHz:               frequency (GHz) [~0.08, 100]
// probability_percent: the probability with which the loss is not exceeded (%) ]0, 100[
// elevAngle_degrees:   elevation angle of the path at the building façade (degrees above the horizontal) ]-90, 90[
// thermally_efficient: is building type thermally efficient or not (traditional)
// [return]:            building entry loss (dB)
double ITURP_2109_2::BuildingEntryLoss(double f_GHz, double probability_percent, double elevAngle_degrees, bool thermally_efficient)
{
    constexpr double BLDG_COEFFS[2][9] = {{12.64, 3.72, 0.96, 9.6, 2.0, 9.1, -3.0, 4.5, -2.0},
	                                      {28.19, -3.00, 8.48, 13.5, 3.8, 27.8, -2.9, 9.4, -2.1}};
	
	int i = 0;
	if( thermally_efficient == true )
		i = 1;
	const double r = BLDG_COEFFS[i][0];
	const double s = BLDG_COEFFS[i][1];
	const double t = BLDG_COEFFS[i][2];
	const double u = BLDG_COEFFS[i][3];
	const double v = BLDG_COEFFS[i][4];
	const double w = BLDG_COEFFS[i][5];
	const double x = BLDG_COEFFS[i][6];
	const double y = BLDG_COEFFS[i][7];
	const double z = BLDG_COEFFS[i][8];

	const double C = -3.0;
	const double logf = log10(f_GHz);
	const double Lh = r + s*logf + t*logf*logf;
	const double Le = 0.212*std::abs(elevAngle_degrees);
	const double mu1 = Lh + Le;
	const double mu2 = w + x*logf;
	const double sigma1 = u + v*logf;
	const double sigma2 = y + z*logf;
	const double FinvP = ITURP_1057_7::Finv(probability_percent/100.0);
	const double AP = FinvP*sigma1 + mu1;
	const double BP = FinvP*sigma2 + mu2;

	const double LomniBEL = 10.0*log10(pow(10.0, 0.1*AP) + pow(10.0, 0.1*BP) + pow(10.0, 0.1*C));

	return LomniBEL;
}
