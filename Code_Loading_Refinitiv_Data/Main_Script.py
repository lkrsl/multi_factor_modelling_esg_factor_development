##################################### (0) Import Packages #####################################

# General Packages
import pandas as pd
import os

os.chdir(r'C:\Users\mauri\Desktop\Uni\1_MSc_Data_Science_in_Business_and_Economics\3_Semester\B560_Advanced_Topics_in_Asset_Management\Project\Part2_Fama_MacBeth')

# Data API
import refinitiv.data as rd

from Functions_Index_Constituents import * 
from Functions_Loading_Data import * 
from Functions_Creating_XLSX import * 
##################################### (I) Open Refinitiv Connection #####################################

rd.open_session() 

##################################### (II) Load Constituents #####################################

data_request = {
    
        "0#.SPX": ["20241031", 1],
        "0#.SP400": ["20241031", 1],
        "0#.SPCY": ["20241031", 1]
}

constituents = getMultipleIndicesConstituents(data_request)
constituents.to_csv("Output_Data/constituents.csv", index = False, sep = ",")

##################################### (III) Load Time Series Data #####################################


monthly_data_fields = [
    "TR.TotalReturn",
    "TR.CompanyMarketCap"
]

#   Interval can be any of these:
#   
#   "daily", "1d", "1D", 
#   "7D", "7d", "weekly", "1W", 
#   "monthly", "1M", 
#   "quarterly", "3M", "6M", 
#   "yearly", "12M", "1Y"
#
#   IMPORTANT: Retrieving intraday data (hourly, minutes, etc.) is not supported in this script! 
#

monthly_time_series_data = getIndexTimeSeries(index_data = constituents, 
                                            index = ["0#.SPX", "0#.SP400", "0#.SPCY"], 
                                            fields = monthly_data_fields, 
                                            start_date = "2009-01-01", 
                                            end_date = "2024-10-31", 
                                            frequency = "monthly", 
                                            dataset_prefix = "monthly_time_series_data",
                                            sleep_time = 2, 
                                            message_interval = 0.05,
                                            saving_interval = 0.01)

##################################### (IV) Exporting XLSX Files #####################################

value_column_dictionary = {
        "Total Return": "ReturnTotal",
        "Company Market Cap": "MCAP"
}



monthly_time_series_data["Date"] = pd.to_datetime(monthly_time_series_data["Date"])
monthly_time_series_data["Date"] = (monthly_time_series_data["Date"] + pd.offsets.MonthEnd(0)).dt.strftime('%Y-%m-%d')

exportTimeSeriesDataAsXLSX(time_series_data = monthly_time_series_data, 
                           value_column_dictionary = value_column_dictionary, 
                           output_file_name = "Output_Data/Stock_Data_Wide_Format")

##################################### (I) Close Refinitiv Connection #####################################

rd.close_session() 
