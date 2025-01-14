##################################### (I) Import Packages #####################################

# General Packages
import pandas as pd

##################################### (II) Functions to Export Data #####################################

def exportTimeSeriesDataAsXLSX(time_series_data, value_column_dictionary, output_file_name):
    
    #Export Transposed Data as Excel Sheet
    with pd.ExcelWriter(output_file_name + ".xlsx", engine="openpyxl") as writer:
        
        #Loops over all columns that should be exported
        for value_column, excel_sheet_name in value_column_dictionary.items():
            
            #Get prepared Data
            transposed_data = getPreparedTimeSeriesDataForXLSXExport(time_series_data, value_column)
            
            #Export prepared Data to Excel Sheet 
            transposed_data.to_excel(writer, sheet_name = excel_sheet_name)        

##################################### (III) Helper Functions #####################################

#Function is used to prepare dataframe for export to excel file
def getPreparedTimeSeriesDataForXLSXExport(time_series_data, value_column):
    
    #Subsets data to wanted column
    data_subsetted = time_series_data[["Date", "Stock", value_column]]
    
    data_subsetted = data_subsetted.dropna() #Drops missing values
    data_subsetted = data_subsetted[data_subsetted[value_column] != ""] #Removes empty strings
    data_subsetted = data_subsetted[data_subsetted[value_column] != "NaN"] #Removes strings with NaN
    
    #Checks for duplicate values and reports if there are any.
    #Duplicate values are dropped and only first value is kept
    duplicates = data_subsetted.duplicated(subset=["Date", "Stock"])
    
    if duplicates.any():
        print("The data contained duplicate values. They will be removed from the data! Here is an overview:")
        print(data_subsetted[duplicates])
        
        data_subsetted = data_subsetted.drop_duplicates(subset=["Date", "Stock"])
        
    #Data is tranposed
    transposed_data = data_subsetted.pivot(index = "Date", columns = "Stock", values = value_column)
    
    return transposed_data
        

#This is a helper function to combine multiple dataframes to one in order to export all data to an excel file at once
def mergeTimeSeriesData(time_series_dataframes, merge_columns):
    
    #Gets first dataframe list
    final_data = time_series_dataframes[0]
    
    #Loops over all dataframes and merges them in one
    for data in time_series_dataframes[1:]:
        final_data = pd.merge(final_data, data, on = merge_columns, how = "outer")
        
    return final_data