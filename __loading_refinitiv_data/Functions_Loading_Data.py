##################################### (I) Import Packages #####################################

# General Packages
import pandas as pd
import time #To calculate time remaining
import os

# Data API
import refinitiv.data as rd

output_folder = "Output_Data"
exceptional_sleep_time = 5

supported_frequency_formats = ["daily", "1d", "1D", "7D", "7d", "weekly", "1W", "monthly", "1M", "quarterly", "3M", "6M", "yearly", "12M", "1Y"]

##################################### (II) Functions to Load Data #####################################

#   This function loads time series data for a given set of fields for a specific stock (Doesn't support hourly information)
def getStockTimeSeriesData(stock, fields, start_date, end_date, frequency, attempt = 1):
    
    if frequency in supported_frequency_formats:
    
        #   The try-except prevents any errors that occur while retrieving data. 
        #   In case of an error, the script will make 2 more attempts at retriving the data.
        #   If all attempts are unsuccessful, the script moves on to the next stock. 
        
        #Retrieve Data    
        try:
        
            time_series = rd.get_history(stock, fields = fields, interval = frequency, start = start_date, end = end_date)
            
            #Adds column with stock name
            time_series["Stock"] = stock
            
            #Adds date column & removes any specific time time information 
            time_series["Date"] = time_series.index.date
            
            time_series = time_series.reset_index(drop = True)
            
        except:
            #Trying again to get data 2 more times
            if attempt >= 1 and attempt <= 3:
                print(f"Attempt {attempt}, Stock {stock} is experiencing issues! Trying again ... ")
                
                #Wait a until sleep time is over and try again to load data for stock!
                time.sleep(exceptional_sleep_time)
                time_series = getStockTimeSeriesData(stock, fields, start_date, end_date, frequency, attempt = attempt + 1)
                
            #After 3 times, script moves on to next stock and returns empty dataframe. 
            elif attempt > 3:
                print(f"Failed to retrieve data for {stock}! Moving on to next stock!")
                
                time_series = pd.DataFrame()
                
                return time_series
    
        #Returns dataframe and drops index
        return time_series
    
    else:
        print(f"Frequency Format not Supported! Please choose any one of these: {supported_frequency_formats}")
        
        time_series = pd.DataFrame()
        
        return time_series

#   This function returns the time series information given by the fields list for a list of stocks (i.e. an index)
def getIndexTimeSeries(index_data, index, fields, start_date, end_date, frequency, dataset_prefix, sleep_time, message_interval, saving_interval):
    
    if frequency in supported_frequency_formats:
    
        #Loads all columns that we want to look at (i.e each index)
        index_data = index_data[index]
        
        #Creates an empty time series table with a column called "Date"
        time_series_data = pd.DataFrame()
        
        #Adds all constituents we want to get data from to a list
        constituents = index_data.stack().tolist()
        
        #Gets number of stocks in index used for message & saving intervals
        number_constituents = len(constituents)
        
        #Contingency for the case that previous data loading failed
        if os.path.exists(os.path.join(output_folder, f"TEMP_remaining_constituents_{index}.csv")) and os.path.exists(os.path.join(output_folder, f"{dataset_prefix}_{index}.csv")):
                
            #Only if both a time series file and a file with remaining stocks exists, we load them as basis to work with
            time_series_data = pd.read_csv(f"{output_folder}/{dataset_prefix}_{index}.csv")
            constituents = pd.read_csv(f"{output_folder}/TEMP_remaining_constituents_{index}.csv")["Remaining_Constituents"].tolist()
    
        #Gets number of stocks in index used for calculating remaining stocks
        number_remaining_constituents = len(constituents)
    
        #Setting Start Time to print remaining processing time
        start_time = time.time()
        
        #Loop over list of stocks
        for constituents_processed, stock in enumerate(constituents):
            
            print(f"Loading Data for {stock} ...")
            
            #Gets data of current stock
            time_series_stock_data = getStockTimeSeriesData(stock, fields, start_date, end_date, frequency)
            
            #Appends data of current stock to new dataframe
            time_series_data = pd.concat([time_series_data, time_series_stock_data], ignore_index=True)
            
            #Gets list of remaining stocks that haven't been processed. This is done to save the list as csv based on saving interval
            remaining_stocks = constituents[(constituents_processed + 1):]
            
            #Prints data loading status for required interval
            # (constituents_processed + 1) because index starts with 0
            printStatus(
                start_time = start_time, 
                number_constituents = number_remaining_constituents, 
                constituents_processed = (constituents_processed + 1), 
                message_interval = round(number_constituents * message_interval, 0))
            
            #Saves current time series as csv as backup. 
            saveCurrentWorkload(
                current_dataset = time_series_data, 
                index = index, 
                dataset_prefix = dataset_prefix, 
                remaining_stocks_list = remaining_stocks, 
                constituents_processed = (constituents_processed + 1), 
                saving_interval = round(number_constituents * saving_interval, 0))
            
            #Set Sleep Timer
            time.sleep(sleep_time)
            
        #Drop temporary remaining stocks file if it exists
        if os.path.exists(os.path.join(output_folder, f"TEMP_remaining_constituents_{index}.csv")):
            os.remove(os.path.join(output_folder, f"TEMP_remaining_constituents_{index}.csv"))
            
        return time_series_data
    else:
        print(f"Frequency Format not Supported! Please choose any one of these: {supported_frequency_formats}")
        
        time_series_data = pd.DataFrame()
        
        return time_series_data

##################################### (III) Helper Functions #####################################

#Saves current time series for a given interval. This is done to prevent data loss in case something goes wrong
def saveCurrentWorkload(current_dataset, index, dataset_prefix, remaining_stocks_list, constituents_processed, saving_interval):
    
    if constituents_processed % saving_interval == 0:    
        remaining_stocks = pd.DataFrame(remaining_stocks_list, columns = ["Remaining_Constituents"])
        
        current_dataset.to_csv(f"{output_folder}/{dataset_prefix}_{index}.csv", index = False, sep = ",")
        remaining_stocks.to_csv(f"{output_folder}/TEMP_remaining_constituents_{index}.csv", index = False, sep = ",")
    
#Returns estimated remaining time for processing data based on average time used for processing so far
def getRemainingTimeEstimate(time_passed, constituents_processed, constituents_remaining):
    
    #Calculate average time per item 
    average_time_per_item = time_passed / constituents_processed
    
    return average_time_per_item * constituents_remaining

#Prints current status of how many constituents were processed and how much time is remaining
def printStatus(start_time, number_constituents, constituents_processed, message_interval):
    
    #Loads current time & calculates time passed
    current_time = time.time()
    time_passed = current_time - start_time
        
    #Calculates items remaining
    constituents_remaining = number_constituents - constituents_processed
        
    #Only prints message for given interval
    if constituents_processed % message_interval == 0:
        if constituents_remaining == 0:
            
            print("################################################")
            print("")
            print(f"Data loading finished! Total processing time: {round(time_passed / 60, 2)} Minutes!")
            print("")
            print("################################################")
        else:
            time_remaining = round(getRemainingTimeEstimate(time_passed, constituents_processed, constituents_remaining) / 60, 2)
            
            print("################################################")
            print("Data Stats:")
            print("")
            print(f"Number of Constituents Loaded: {constituents_processed}")
            print(f"Number of Constituents Remaining: {constituents_remaining}")
            print("")
            print(f"Estimated Time Remaining: {time_remaining} Minutes")
            print("################################################")
        
        
    
    


