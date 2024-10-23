"""
@author: laura kreisel and amelie bescherer
date: 19.10.2024
"""
#Import packages
from shiny import ui, render, App, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.correlation_tools import cov_nearest 
from sklearn.covariance import LedoitWolf

#Load files
ff_data = pd.read_csv('fama_french_data.csv', index_col='date', parse_dates=True)
mcap_data = pd.read_csv('mktcap.csv', index_col='ticker')

#Ui 
app_ui = ui.page_fluid(
    # Heading
    ui.markdown("<h1 style='text-align: center; font-size: 24px;'>ESG-Driven Portfolio Optimization: Personalized Factor Investing Dashboard</h1>"),
    ui.markdown("<h2 style='text-align: center; font-size: 12px;'>Authors: Laura Kreisel and Amelie Bescherer</h2>"),
    ui.output_text_verbatim("value"),
    
    # Description 
    ui.div(
        ui.input_text_area(
        id="caption_regular",
        label="Description",
        value=("This interactive dashboard empowers investors to create personalized portfolios aligned with their ESG preferences and risk tolerance. "
               "Users can adjust sliders for Environmental, Social, and Governance factors, set their risk aversion level, and exclude specific sectors or stocks. "
               "The tool leverages the Fama-French 3-Factor Model for return predictions and employs the Black-Litterman approach for portfolio optimization. "
               "By combining quantitative finance techniques with ESG considerations, this dashboard offers a sophisticated yet user-friendly approach to "
               "sustainable investing, allowing users to visualize how their preferences translate into a tailored investment strategy."),
        width="100%"
    ),
    style="background-color: #f0f0f0; border-radius: 5px; padding: 10px; margin-bottom: 10px; width: 100%;"
    ),

    # Subheading "Selection Panel"
    ui.markdown("<h4 style='text-align: left; color: #808080;'>Selection Panel</h4>")
)


#Server logic
def server(input, output, session):
    @reactive.Calc
    def process_data():
        # This function will process the data based on user inputs
        # For now, it's just a placeholder
        return ff_data

    @output
    @render.text
    def value():
        # This function will return a text output
        # For now, it's just a placeholder
        return "Data loaded successfully. Ready for analysis."

    @reactive.Effect
    @reactive.event(input.caption_regular)
    def _():
        # This effect will trigger when the caption is changed
        # For now, it's just a placeholder
        print("Caption updated")
    
app = App(app_ui, server)

#Note on Usage: To run on Windows, put this command into the terminal: shiny run --reload data_analysis_esg_factor_investing.py
#Declaration: This document was created by ourselfs, hereby acknowledging that this submission is my own work. However, we have used basic idees from several sources.