# Stock-Analysis-with-Python
This repository consists of the python code used for both fundamental and technical analysis for all the US stocks.

Yahoo Finance data is used for simple stocks tickers extraction (free)

Financial Modeling Prep data is used for analysis (I have a paid subscription plan in this)
Refer to https://site.financialmodelingprep.com/ for more information

Both fundamental and technical analysis code will be included in this repo eventually. 
Fundamental: Earning, revenue, profit margin analysis would be performed
Technical: 
a. Calculate the relative strength of the stocks with respect to the stock market index (S&P 500 is used in this case). Refer to https://www.investopedia.com/terms/r/relativestrength.asp for more information.
b. Use Mark Minervini Trend template conditions and rank the stocks accordingly
c. Use the ranking system to focus on stocks that has at least 7 (out of 8) and do further analysis with it

Use the code in this sequence:
1. get_company_list.py -> Extract the complete list of US stocks, including those in the 3 major indices (S&P 500, Nasdaq and Dow), do note that there is some filter after that to remove some stocks that I am not interested (penny stocks, funds and etc)
2. price_sub.py -> Extract the price data with Financial Modeling Prep, calculate the relative strength of all the stocks (compare them against S&P 500 and rank them), use Mark Minervini's trend template to rank stocks. 
