##################################### (I) Import Packages #####################################

# General Packages
import pandas as pd

# Data API
import refinitiv.data as rd

##################################### (II) Functions #####################################

#
#   ERROR: parameters Option actually doesn't return the constituents on a specific date. 
#


#
#   This function returns the constituents of an index on a given date.
# 

def getSingleIndexConstituents(date, index):
    
   #Retrieves constituents
   data = rd.get_data(index, ["TR.RIC"], parameters = {"date": date})
   
   #Rename column with constituents with index name
   data = data.rename(columns={"Instrument": index})
   
   #Drop not needed column
   data = data.drop(columns=["RIC"])

   return data

#
#   This function returns the constituents of multiple given indices and adds them together in a single dataframe
#

def getMultipleIndicesConstituents(indices_dictionary):
    
    #Creates empty list for dataframes with index constituents
    single_index_constitutents = []
    
    #Loops over indices
    for index, keys in indices_dictionary.items():
        
        #Loads parameters
        date = keys[0]
        sample = keys[1]
        
        #Reads data & takes sample
        constituents = getSingleIndexConstituents(date, index)
        constituents_sample = constituents.sample(frac = sample)
        
        #Appends sample to list
        single_index_constitutents.append(constituents_sample)
            
    #Gets base dataframe 
    data = single_index_constitutents[0]
    
    #If there are multiple dataframes, we merge them together based on their date
    if len(single_index_constitutents) > 1:
        for single_index_constitutent in single_index_constitutents[1:]:
    
               data = pd.merge(single_index_constitutent, data, left_index=True, right_index=True, how = "outer")
           
    return data.reset_index(drop=True)