# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
Queries the interpolation service of the the ITU-R Geospatial Catalog.

See https://br-geoportal.itu.int/ITU-R/BR-GeoCatalogue/BR-GeoApi/
"""

from propakai.geo_catalog import gc_p452_18
from propakai.geo_catalog import gc_p453_14
from propakai.geo_catalog import gc_p530_19
from propakai.geo_catalog import gc_p534_6
from propakai.geo_catalog import gc_p617_6
from propakai.geo_catalog import gc_p678_3
from propakai.geo_catalog import gc_p834_9
from propakai.geo_catalog import gc_p835_7
from propakai.geo_catalog import gc_p836_6
from propakai.geo_catalog import gc_p837_8
from propakai.geo_catalog import gc_p839_4
from propakai.geo_catalog import gc_p840_9
from propakai.geo_catalog import gc_p1510_1
from propakai.geo_catalog import gc_p1511_3
from propakai.geo_catalog import gc_p1546_6
from propakai.geo_catalog import gc_p1812_8
from propakai.geo_catalog import gc_p1853_2
from propakai.geo_catalog import gc_p2001_6
from propakai.geo_catalog import gc_p2145_0
from propakai.geo_catalog import gc_p2148_0


if __name__ == '__main__':
    lat = 45.0
    lon = -75.0
    month = 7
    p = 50
    print(f'\nUsing lat={lat:.3f}, lon={lon:.3f}, month={month} (when applicable), ' \
          f'p={p:.1f}% (when applicable).')

    print('\nP.452-18')
    print(f'  ΔN: {gc_p452_18.avg_refractivity_gradient_1km(lat, lon):.3f} N-units/km')
    print(f'  N0: {gc_p452_18.avg_sea_level_surface_refractivity(lat, lon):.3f} N-units')

    print('\nP.453-14')
    print(f'  Annual Nwet: {gc_p453_14.annual_surface_refractivity_wet_term(lat, lon, p):.2f} ppm')
    print(f'  Monthly Nwet: {gc_p453_14.monthly_surface_refractivity_wet_term(lat, lon, p, month):.2f} ppm')
    print(f'  Annual ΔN_1km: {gc_p453_14.annual_refractivity_gradient_1km(lat, lon, p):.2f} N-units/km')
    print(f'  Monthly ΔN_1km: {gc_p453_14.monthly_refractivity_gradient_1km(lat, lon, p, month):.2f} N-units/km')
    print(f'  Annual ΔN_65m: {gc_p453_14.annual_refractivity_gradient_65m(lat, lon, p):.2f} N-units/km')
    print(f'  Monthly ΔN_65m: {gc_p453_14.monthly_refractivity_gradient_65m(lat, lon, p, month):.2f} N-units/km')
    print(f'  Annual β: {gc_p453_14.percentage_annual_time_beta(lat, lon):.2f} %')
    print(f'  Monthly β: {gc_p453_14.percentage_monthly_time_beta(lat, lon, month):.2f} %')
    print(f'  Ss: {gc_p453_14.surface_ducts_avg_annual_stats(lat, lon, gc_p453_14.SModelParam.STRENGTH):.2f} M-units')
    print(f'  Et: {gc_p453_14.elevated_ducts_avg_year_stats(lat, lon, gc_p453_14.EModelParam.THICKNESS):.2f} m')
    print(f'  Land-sea mask: {gc_p453_14.land_sea_mask(lat, lon)}')

    print('\nP.530-19')
    print(f'  dN75: {gc_p530_19.avg_worst_month_refractivity_gradient_75m(lat, lon):.3f} N-units')
    print(f'  logK: {gc_p530_19.log10_geoclimatic_factor(lat, lon):.3f}')

    print('\nP.534-6')
    print(f'  foEs: {gc_p534_6.sporadic_e_critical_frequency(lat, lon, p):.3f} MHz')

    print('\nP.617-6')
    print(f'  ΔN: {gc_p617_6.avg_refractivity_gradient_1km(lat, lon):.3f} N-units/km')
    print(f'  N0: {gc_p617_6.avg_sea_level_surface_refractivity(lat, lon):.3f} N-units')

    print('\nP.678-3')
    print(f'  rc: {gc_p678_3.climatic_ratio(lat, lon):.3f}')

    print('\nP.834-9')
    print(f'  href: {gc_p834_9.avg_height_reference_level(lat, lon):.2f} m')
    print(f'  A0h: {gc_p834_9.coefficients(lat, lon, gc_p834_9.Coefficient.A0H):.3f}')
    print(f'  avg λ: {gc_p834_9.vapour_pressure_decrease_factor(lat, lon, gc_p834_9.ModelParam.AVERAGE_VALUE):.3f}')
    print(f'  avg ps: {gc_p834_9.air_total_pressure(lat, lon, gc_p834_9.ModelParam.AVERAGE_VALUE):.3f} hPa')
    print(f'  avg es: {gc_p834_9.water_vapour_partial_pressure(lat, lon, gc_p834_9.ModelParam.AVERAGE_VALUE):.3f} hPa')
    print(f'  avg αm: {gc_p834_9.lapse_rate_mean_temperature_of_water_vapour(lat, lon, gc_p834_9.ModelParam.AVERAGE_VALUE):.3f} K/km')
    print(f'  avg Tms: {gc_p834_9.mean_temperature_water_vapour(lat, lon, gc_p834_9.ModelParam.AVERAGE_VALUE):.3f} K')

    # Not Functional
    #print('\nP.835-7')
    #print(f'  Annual Z: {gc_p835_7.annual_geometric_altitude(lat, lon, altitude_level=1):.2f} km')
    #print(f'  Monthly Z: {gc_p835_7.monthly_geometric_altitude(lat, lon, altitude_level=1, month=month):.2f} km')

    print('\nP.836-6')
    print(f'  Annual vsch: {gc_p836_6.annual_water_vapour_scale_height(lat, lon, p):.3f} km')
    print(f'  Monthly vsch: {gc_p836_6.monthly_water_vapour_scale_height(lat, lon, p, month):.3f} km')
    print(f'  Annual rho: {gc_p836_6.annual_surface_water_vapour_density(lat, lon, p):.3f} g/m3')
    print(f'  Monthly rho: {gc_p836_6.monthly_surface_water_vapour_density(lat, lon, p, month):.3f} g/m3')
    print(f'  Annual V: {gc_p836_6.annual_total_columnar_water_vapour_content(lat, lon, p):.3f} kg/m2')
    print(f'  Monthly V: {gc_p836_6.monthly_total_columnar_water_vapour_content(lat, lon, p, month):.3f} kg/m2')
    print(f'  alt: {gc_p836_6.topographic_altitude(lat, lon):.3f} km')

    print('\nP.837-8')
    print(f'  R0_01: {gc_p837_8.annual_rainfall_rate_001(lat, lon):.1f} mm/hr')
    print(f'  MT: {gc_p837_8.total_monthly_mean_rainfall(lat, lon, month):.1f} mm')

    print('\nP.839-4')
    print(f'  hR: {gc_p839_4.mean_annual_rain_height(lat, lon):.3f} km amsl')

    print('\nP.840-9')
    print(f'  PL: {gc_p840_9.log_normal_approximation_params(lat, lon, gc_p840_9.ModelParam.PROBABILITY):.3f}')
    print(f'  Annual L: {gc_p840_9.annual_integrated_cloud_liquid_water_content(lat, lon, gc_p840_9.ModelParam.PROBABILITY, p):.3f} kg/m2')
    print(f'  Monthly L: {gc_p840_9.monthly_integrated_cloud_liquid_water_content(lat, lon, month, gc_p840_9.ModelParam.PROBABILITY, p):.3f} kg/m2')

    print('\nP.1510-1')
    print(f'  TAnnual: {gc_p1510_1.annual_mean_surface_temperature(lat, lon):.1f} K')
    print(f'  Tii: {gc_p1510_1.monthly_mean_surface_temperature(lat, lon, month):.1f} K')

    print('\nP.1511-3')
    print(f'  h_topo: {gc_p1511_3.topographic_height(lat, lon):.2f} m')
    print(f'  h_EGM2008: {gc_p1511_3.geoid_undulation(lat, lon):.2f} m')

    print('\nP.1546-6')
    print(f'  dN: {gc_p1546_6.radio_refractivity_gradient(lat, lon, p):.3f} N-units/km')

    print('\nP.1812-8')
    print(f'  ΔN: {gc_p1812_8.avg_refractivity_gradient_1km(lat, lon):.3f} N-units/km')
    print(f'  N0: {gc_p1812_8.avg_sea_level_surface_refractivity(lat, lon):.3f} N-units')

    print('\nP.1853-2')
    print(f'  Pannual: {gc_p1853_2.annual_mean_surface_pressure(lat, lon):.3f} hPa')
    print(f'  WVannual: {gc_p1853_2.annual_mean_surface_water_vapour_density(lat, lon):.3f} g/m3')

    print('\nP.2001-6')
    print(f'  Nd1km50: {gc_p2001_6.median_avg_refractivity_gradient_1km(lat, lon):.3f} N-units')
    print(f'  S∆Nsup: {gc_p2001_6.supslope_avg_refractivity_gradient_1km(lat, lon):.3f} N-units')
    print(f'  S∆Nsub: {gc_p2001_6.subslope_avg_refractivity_gradient_1km(lat, lon):.3f} N-units')
    print(f'  Nd65m1: {gc_p2001_6.refractivity_gradient_65m(lat, lon):.3f} N-units')
    print(f'  Pr6: {gc_p2001_6.probability_of_rain_6h(lat, lon):.3f}')
    print(f'  MT: {gc_p2001_6.annual_rainfall_accumulation(lat, lon):.3f} mm')
    print(f'  βrain: {gc_p2001_6.beta_rain_ratio(lat, lon):.3f}')
    print(f'  h0: {gc_p2001_6.mean_annual_0c_isotherm_height(lat, lon):.3f} km amsl')
    print(f'  ρsur: {gc_p2001_6.surface_water_vapour_density(lat, lon):.3f} g/m3')
    print(f'  foEs: {gc_p2001_6.sporadic_e_critical_frequency(lat, lon, p):.3f} MHz')
    print(f'  Climatic zone: {gc_p2001_6.climatic_zone(lat, lon)}')

    print('\nP.2145-0')
    print(f'  Annual Ps: {gc_p2145_0.annual_surface_total_pressure(lat, lon, p):.3f} hPa')
    print(f'  Annual Ts: {gc_p2145_0.annual_surface_temperature(lat, lon, p):.3f} K')
    print(f'  Annual ρws: {gc_p2145_0.annual_surface_water_vapour_density(lat, lon, p):.3f} g/m3')
    print(f'  Annual Vs: {gc_p2145_0.annual_integrated_water_vapour_content(lat, lon, p):.3f} kg/m2')
    print(f'  Annual P̅s: {gc_p2145_0.annual_surface_total_pressure_stats(lat, lon, gc_p2145_0.ModelParam.MEAN):.3f} hPa')
    print(f'  Annual σTs: {gc_p2145_0.annual_surface_temperature_stats(lat, lon, gc_p2145_0.ModelParam.STD_DEV):.3f} K')
    print(f'  Annual ρ̅ws: {gc_p2145_0.annual_surface_water_vapour_density_stats(lat, lon, gc_p2145_0.ModelParam.MEAN):.3f} g/m3')
    print(f'  Annual σVs: {gc_p2145_0.annual_integrated_water_vapour_content_stats(lat, lon, gc_p2145_0.ModelParam.STD_DEV):.3f} kg/m2')
    print(f'  Annual psch: {gc_p2145_0.annual_surface_total_pressure_scale_height(lat, lon):.3f}')
    print(f'  Annual tsch: {gc_p2145_0.annual_surface_temperature_scale_height(lat, lon):.3f}')
    print(f'  Annual vsch: {gc_p2145_0.annual_water_vapour_scale_height(lat, lon):.3f}')
    print(f'  Monthly Ps: {gc_p2145_0.monthly_surface_total_pressure(lat, lon, p, month):.3f} hPa')
    print(f'  Monthly Ts: {gc_p2145_0.monthly_surface_temperature(lat, lon, p, month):.3f} K')
    print(f'  Monthly ρws: {gc_p2145_0.monthly_surface_water_vapour_density(lat, lon, p, month):.3f} g/m3')
    print(f'  Monthly Vs: {gc_p2145_0.monthly_integrated_water_vapour_content(lat, lon, p, month):.3f} kg/m2')
    print(f'  Monthly P̅s: {gc_p2145_0.monthly_surface_total_pressure_stats(lat, lon, gc_p2145_0.ModelParam.MEAN, month):.3f} hPa')
    print(f'  Monthly σTs: {gc_p2145_0.monthly_surface_temperature_stats(lat, lon, gc_p2145_0.ModelParam.STD_DEV, month):.3f} K')
    print(f'  Monthly ρ̅ws: {gc_p2145_0.monthly_surface_water_vapour_density_stats(lat, lon, gc_p2145_0.ModelParam.MEAN, month):.3f} g/m3')
    print(f'  Monthly σVs: {gc_p2145_0.monthly_integrated_water_vapour_content_stats(lat, lon, gc_p2145_0.ModelParam.STD_DEV, month):.3f} kg/m2')
    print(f'  Monthly psch: {gc_p2145_0.monthly_surface_total_pressure_scale_height(lat, lon, month):.3f}')
    print(f'  Monthly tsch: {gc_p2145_0.monthly_surface_temperature_scale_height(lat, lon, month):.3f}')
    print(f'  Monthly vsch: {gc_p2145_0.monthly_water_vapour_scale_height(lat, lon, month):.3f}')
    print(f'  Zground: {gc_p2145_0.surface_height(lat, lon):.3f} m')
    print(f'  λVs: {gc_p2145_0.weibull_scale_parameter(lat, lon):.3f}')
    print(f'  kVs: {gc_p2145_0.weibull_shape_parameter(lat, lon):.3f}')

    print('\nP.2148-0')
    print(f'  W: {gc_p2148_0.average_annual_wind_speed(lat, lon, p):.3f} m/s')

    print('')
