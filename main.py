import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from constants import quant_holdings, parakh_parigh_holdings

class MutualFundNAVTracker:
    def __init__(self, fund_holdings):
        self.holdings = fund_holdings
        
    def get_stock_prices(self):
        percent_changes = {}
        
        for stock, weight in self.holdings.items():
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=2)
                
                stock_data = yf.download(stock, start=start_date, end=end_date+timedelta(days=1))
                
                if stock_data.empty:
                    st.warning(f"No data available for {stock}")
                    percent_changes[stock] = 0
                    continue
                
                stock_data = stock_data.sort_index()
                valid_closes = stock_data['Close'].dropna()
                
                if len(valid_closes) < 2:
                    st.warning(f"Insufficient historical data for {stock}")
                    percent_changes[stock] = 0
                    continue
                
                previous_close = valid_closes.iloc[-2]
                current_close = valid_closes.iloc[-1]
                
                percent_change = ((current_close - previous_close) / previous_close) * 100
                percent_changes[stock] = percent_change
                
            except Exception as e:
                st.error(f"Error fetching data for {stock}: {e}")
                percent_changes[stock] = 0
        
        return pd.Series(percent_changes)
    
    
    def get_detailed_breakdown(self):
        percent_changes = self.get_stock_prices()
        
        breakdown = []
        all_contributions = []
        for stock, weight in self.holdings.items():
            stock_change = float(percent_changes.get(stock, 0))
            contribution = weight * stock_change
            all_contributions.append(contribution)
            breakdown.append({
                'Stock': stock, 
                'Weight': f"{weight}%", 
                'Daily Change': f"{stock_change:.2f}%", 
                'NAV Contribution': f"{contribution:.4f}%",
                'Cumulative NAV Contribution': f"{np.sum(all_contributions):.4f}%"
            })
        
        return breakdown

def main():
    st.title('Mutual Fund NAV Calculator')
    
    fund_options = {
        'Quant Small Cap Fund': quant_holdings,
        'Parakh Parigh Flexi Cap Fund': parakh_parigh_holdings
    }
    
    selected_fund = st.selectbox('Select Fund', list(fund_options.keys()))
    
    if st.button('Calculate NAV'):
        nav_tracker = MutualFundNAVTracker(fund_options[selected_fund])
        
        st.subheader('Detailed Breakdown')
        breakdown_df = pd.DataFrame(nav_tracker.get_detailed_breakdown())

        nav_change = float(breakdown_df['Cumulative NAV Contribution'].iloc[-1][:-1])/100
        nav_change = f"{nav_change:.4f}"
        
        st.metric('Total NAV Change', f'{nav_change}%')
        
        st.dataframe(breakdown_df)
        

if __name__ == '__main__':
    main()