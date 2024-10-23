from shiny import ui, render, App, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.correlation_tools import cov_nearest 
from sklearn.covariance import LedoitWolf

app_ui = ui.page_fluid(
    ui.h2("ESG Asset Allocation Application"),
    ui.p("Luc C. Smith & Samuel M. Reisgys"),
    ui.hr(),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("env_score", "Environmental (E) Score", 0, 100, 50),
            ui.p("Ex: gas emissions, anti-pollution actions, regulatory tests, etc. (100 being the most care)", class_="text-muted"),
            ui.input_slider("social_score", "Social (S) Score", 0, 100, 50),
            ui.p("Ex: child labor, ethical policies, employee unionization, etc. (100 being the most care)", class_="text-muted"),
            ui.input_slider("gov_score", "Governance (G) Score", 0, 100, 50),
            ui.p("Ex: fairness, corruption, compensation of employees, bias, etc. (100 being the most care)", class_="text-muted"),
            ui.input_slider("risk_aversion", "Risk Aversion", 0, 5, 2.5, step=0.1),
            ui.p("5 avoiding most risk, 0 taking most risk", class_="text-muted"),
            ui.input_text("exclude_sectors", "Sectors to Exclude (comma-separated)"),
            ui.input_text("exclude_stocks", "Stocks to Exclude (comma-separated)"),
            ui.input_action_button("confirm", "Confirm Values"),
            ui.input_action_button("show_sectors", "See sector names"),
            ui.input_action_button("create_portfolio", "Create Portfolio"),
        ),
        ui.column(8,
            ui.output_text("selected_values"),
            ui.output_plot("portfolio_chart"),
            ui.output_text("loading_text")
        )
    )
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.show_sectors)
    def show_sectors():
        ui.modal_show(ui.modal(
            "Sector names",
            "Communication Services, Consumer, Financials, Health Care, Information Technology, Utilities",
            easy_close=True,
            footer=None
        ))

    @reactive.Calc
    def get_inputs():
        return {
            "env_score": input.env_score(),
            "social_score": input.social_score(),
            "gov_score": input.gov_score(),
            "risk_aversion": input.risk_aversion(),
            "exclude_sectors": input.exclude_sectors(),
            "exclude_stocks": input.exclude_stocks()
        }

    @output
    @render.text
    @reactive.event(input.confirm)
    def selected_values():
        inputs = get_inputs()
        return (f"Selected Values:\nE: {inputs['env_score']} S: {inputs['social_score']} "
                f"G: {inputs['gov_score']} R: {inputs['risk_aversion']}\n"
                f"Excluded sectors: {inputs['exclude_sectors']}\n"
                f"Excluded stocks: {inputs['exclude_stocks']}")

    def getFamaFrench3_returns(stocks):
        ff_data = pd.read_csv('fama_french_data.csv', index_col='date', parse_dates=True)
        ff_data = ff_data.loc[ff_data.index > '2017'].resample('M').last()
        stocks = stocks.loc[stocks.index < '2022-04'].resample('M').last()
        
        excess = stocks.pct_change()
        excess.fillna(method='ffill', inplace=True)                  
        excess.fillna(0, inplace=True)
        excess = excess.subtract(ff_data.RF, axis=0)
        
        factors = ff_data[['Mkt-RF', 'SMB', 'HML']]
        factors = sm.add_constant(factors)
        
        ff_betas = sm.OLS(excess, factors).fit().params
        ff_betas = ff_betas.set_axis(excess.columns, axis=1)
        ff_betas = ff_betas.transpose()
        
        r_f = ff_data.RF.mean()
        mkt_prem = ff_data['Mkt-RF'].mean()
        SMB = ff_data.SMB.mean()
        HML = ff_data.HML.mean()
        ff_betas = ff_betas.set_axis(['const', 'b1', 'b2', 'b3'], axis=1)
        
        e_r = (r_f + ff_betas.b1*mkt_prem + ff_betas.b2*SMB + ff_betas.b3*HML)*12
        
        return e_r

    def BlackLit_opt(prices, risk_a):
        Q = getFamaFrench3_returns(prices)
        Q = Q[Q>-1] 
        
        prices = prices.loc[:, Q.index]
        
        mcap_data = pd.read_csv('mktcap.csv', index_col='ticker')
        mcap_data.index = [stock.split()[0] for stock in mcap_data.index]
        mcap_data = mcap_data.loc[prices.columns]
        mcap_data.fillna(mcap_data.mean(), inplace=True)
        
        mcap_wgts = (mcap_data / mcap_data.sum()).CUR_MKT_CAP.values
        
        A = risk_a
        cov = prices.pct_change().cov()
        
        cov_shrunk = LedoitWolf().fit(cov)
        S = cov_shrunk.covariance_  
        
        pi = 2.0*A*(S@mcap_wgts)
        
        # Further implementation of Black-Litterman model...
        # Return posterior returns and covariance matrix

    @output
    @render.text
    @reactive.event(input.create_portfolio)
    def loading_text():
        return "Creating Portfolio... It may take up to a minute"

    @output
    @render.plot
    @reactive.event(input.create_portfolio)
    def portfolio_chart():
        # Implement your portfolio generation logic here
        # This is a placeholder for the actual chart generation
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Portfolio Chart\n(Placeholder)", ha='center', va='center')
        ax.axis('off')
        return fig

app = App(app_ui, server)


#To run this, put this command into the terminal: shiny run --reload data_analysis.py