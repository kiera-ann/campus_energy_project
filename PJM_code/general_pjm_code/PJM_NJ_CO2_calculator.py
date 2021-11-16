# Calculators for different fuel mixes.

# In order to approximate the emissions for a single kWh of produced
# energy, per power source we look at the following 2019 data sets.

# Detailed EIA-923 emissions survey data
# (https://www.eia.gov/electricity/data/state/emission_annual.xls)


# Net Generation by State by Type of Producer by Energy Source
# (EIA-906, EIA-920, and EIA-923)
# (https://www.eia.gov/electricity/data/state/annual_generation_state.xls)


"""
The 2019 NJ Numbers from "Total Electric Power Industry" Emissions are (metric tons of CO2, SO2, NOx)

Year	State	Producer Type	Energy Source	"CO2 (Metric Tons)"	"SO2 (Metric Tons)"	"NOx (Metric Tons)"
2019	NJ	Total Electric Power Industry	All Sources	18,868,591	2,712	10,191
2019	NJ	Total Electric Power Industry	Coal	1,285,663	1,051	843
2019	NJ	Total Electric Power Industry	Natural Gas	16,646,217	59	4,525
2019	NJ	Total Electric Power Industry	Other Biomass	0	1	3,111
2019	NJ	Total Electric Power Industry	Other Gases	0	3	214
2019	NJ	Total Electric Power Industry	Other	856,460	834	1,385
2019	NJ	Total Electric Power Industry	Petroleum	80,251	764	113

Source: https://www.eia.gov/electricity/data/state/emission_annual.xls

The 2019 NJ Numbers for "Total Electric Power Industry" on power generation are (power in MWh)

YEAR	STATE	TYPE OF PRODUCER	ENERGY SOURCE	GENERATION (Megawatthours)
2019	NJ	Total Electric Power Industry	Total	71,018,774
2019	NJ	Total Electric Power Industry	Coal	1,041,529
2019	NJ	Total Electric Power Industry	Pumped Storage	-93,829
2019	NJ	Total Electric Power Industry	Hydroelectric Conventional	26,468
2019	NJ	Total Electric Power Industry	Natural Gas	40,449,133
2019	NJ	Total Electric Power Industry	Nuclear	26,637,324
2019	NJ	Total Electric Power Industry	Other Gases	216,377
2019	NJ	Total Electric Power Industry	Other	615,725
2019	NJ	Total Electric Power Industry	Petroleum	142,423
2019	NJ	Total Electric Power Industry	Solar Thermal and Photovoltaic	1,164,721
2019	NJ	Total Electric Power Industry	Other Biomass	796,907
2019	NJ	Total Electric Power Industry	Wind	21,996

Source: https://www.eia.gov/electricity/data/state/annual_generation_state.xls
"""

# GENERATION (Megawatthours)
Coal_MWh = 1041529
Natural_Gas_MWh = 40449133
Oil_MWh = 142423  # Petroleum
Other_nonrenewable_MWh = 615725

# Assume 0 for the following since I am unable to deduce what their composition is
#  multiple fuels

# Emissions (metric tons of CO2)
Coal_CO2 = 1285663
Natural_Gas_CO2 = 16646217
Oil_CO2 = 80251  # Petroleum
Other_nonrenewable_CO2 = 856460


def PJM_NJ_CO2_per_MWh() :
    # Determines metric tons of CO2 per Megawatthours
    Coal_CO2_per_MWh = Coal_CO2 / Coal_MWh
    Natural_Gas_CO2_per_MWh = Natural_Gas_CO2 / Natural_Gas_MWh
    Oil_CO2_per_MWh = Oil_CO2 / Oil_MWh  # Petroleum
    Other_nonrenewable_CO2_per_MWh = Other_nonrenewable_CO2 / Other_nonrenewable_MWh

    CO2_intensity_dict = { "units" : "metric tons CO2 per Megawatt hours" ,
                           "coal" : Coal_CO2_per_MWh ,
                           "gas" : Natural_Gas_CO2_per_MWh ,
                           "oil" : Oil_CO2_per_MWh ,
                           "other" : Other_nonrenewable_CO2_per_MWh }

    return CO2_intensity_dict
