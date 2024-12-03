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

constituents = pd.read_csv("Output_Data/constituents.csv")
##################################### (III) Load Time Series Data #####################################

monthly_data_fields_1 = [
    "TR.TotalReturn",
    "TR.CompanyMarketCap",
]

monthly_data_fields_2 = [
    "TR.TRESGScore"
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

monthly_return_data = getIndexTimeSeries(index_data = constituents, 
                                            index = ["0#.SPX", "0#.SP400", "0#.SPCY"], 
                                            fields = monthly_data_fields_1, 
                                            start_date = "2009-01-01", 
                                            end_date = "2024-10-31", 
                                            frequency = "monthly", 
                                            dataset_prefix = "monthly_return_data",
                                            sleep_time = 2, 
                                            message_interval = 0.05,
                                            saving_interval = 0.01)

monthly_esg_data = getIndexTimeSeries(index_data = constituents, 
                                            index = ["0#.SPX", "0#.SP400", "0#.SPCY"], 
                                            fields = monthly_data_fields_2, 
                                            start_date = "2009-01-01", 
                                            end_date = "2024-10-31", 
                                            frequency = "monthly", 
                                            dataset_prefix = "monthly_esg_data",
                                            sleep_time = 2, 
                                            message_interval = 0.05,
                                            saving_interval = 0.01)

##################################### (IV) Exporting XLSX Files #####################################

return_value_column = {
        "Total Return": "ReturnTotal",
        "Company Market Cap": "MCAP",
}

esg_value_column = {
        "ESG Score": "ESG"
}


#Exporting Return Data

monthly_return_data["Date"] = pd.to_datetime(monthly_return_data["Date"])
monthly_return_data["Date"] = (monthly_return_data["Date"] + pd.offsets.MonthEnd(0)).dt.strftime('%Y-%m-%d')

exportTimeSeriesDataAsXLSX(time_series_data = monthly_return_data, 
                           value_column_dictionary = return_value_column, 
                           output_file_name = "Output_Data/Stock_Return_Data_Wide_Format")

#Exporting ESG Data
monthly_esg_data["Date"] = pd.to_datetime(monthly_esg_data["Date"])
monthly_esg_data["Date"] = (monthly_esg_data["Date"] + pd.offsets.MonthEnd(0)).dt.strftime('%Y-%m-%d')

exportTimeSeriesDataAsXLSX(time_series_data = monthly_esg_data, 
                           value_column_dictionary = esg_value_column, 
                           output_file_name = "Output_Data/Stock_ESG_Data_Wide_Format")

##################################### (I) Close Refinitiv Connection #####################################

rd.close_session() 
