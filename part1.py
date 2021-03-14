import datetime as dt
import pandas_datareader as web
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class Portfolio:	
	def __init__(self, basketPortfolio, startDate, endDate, benchmarkTicker):
		"""
		Args:
		    basketPortfolio (dict): stocks in the portfolio and their corresponding number of shares
		    startDate (datetime object): start date of the lifetime of the portfolio
		    endDate (datetime object): end date of the lifetime of the portfolio
		    benchmarkTicker (str): ticker of the portfolio's benchmark index
		"""
		self.basketPortfolio = basketPortfolio

		self.startDate = startDate
		self.endDate = endDate

		self.benchmarkTicker = benchmarkTicker
		self.symbols = list(self.basketPortfolio.keys())

		# Get the historical adjusted close stock prices for the stocks in the portfolio
		self.priceData = web.DataReader(self.symbols, "yahoo" , self.startDate, self.endDate)['Adj Close']
		
		self.priceData['Portfolio Value'] = None
		self.priceData['Daily Returns'] = None

		totalValue = 0

		# Calculate daily portfolio value and daily returns
		for row in range(0, len(self.priceData)): # iterate through rows
			for i in self.basketPortfolio: # iterate through tickers
				totalValue += self.priceData[i].iloc[row] * self.basketPortfolio[i]
			self.priceData['Portfolio Value'].iloc[row] = totalValue
			if row != 0:
				self.priceData['Daily Returns'] = self.priceData['Portfolio Value'].pct_change(1)
			totalValue = 0

	def averageDailyReturn(self):
		"""Used CAGR to calculate the average daily return
		CAGR is a good measure to determine what an investment yields on a daily compounded basis

		CAGR = (final portfolio value/initial portfolio value) ^ (1/business days in between the start date and the end date) - 1
		
		Returns:
		    float: the average daily percent return of the portfolio
		"""
		# The length of the dataframe is the number of trading days in the lifespan of the portfolio
		averageDailyGain = (((self.priceData['Portfolio Value'].iloc[len(self.priceData) - 1])/self.priceData['Portfolio Value'].iloc[0])**(1/len(self.priceData)) - 1)
		return averageDailyGain

	def volatility(self):
		"""Calculate the standard deviation of the daily returns of portfolio value
		Made the variable that is returned a private class variable, so that other methods in the class can access the portfolio volatility value
		
		Returns:
		    float: the portfolio's volatility over the lifespan of the portfolio
		"""
		self.__portfolioVolatility = self.priceData['Daily Returns'].std()
		return self.__portfolioVolatility

	def riskRatio(self):
		"""		
		Returns:
		    float: volatility ratio of the portfolio compared to the volatility of the benchmark over the lifetime of the portfolio
		"""
		# Get the historical adjusted close stock prices for the portfolio's benchmark
		self.benchmarkData = pd.DataFrame(web.DataReader(self.benchmarkTicker, "yahoo" , self.startDate, self.endDate)['Adj Close'])
		self.benchmarkData = self.benchmarkData.assign(DailyReturns = "None")
		
		# Calculate daily returns of the benchmark index
		for row in range(0, len(self.benchmarkData)):
			self.benchmarkData['DailyReturns'] = self.benchmarkData['Adj Close'].pct_change(1)

		# Calculate standard deviation of the benchmark's daily returns
		self.__benchmarkVolatility = self.benchmarkData['DailyReturns'].std()

		# Risk Ratio = Portfolio Volatility/Benchmark Volatility
		return self.__portfolioVolatility/self.__benchmarkVolatility

	def marginalVolatility(self, ticker, shares):
		"""
		Args:
		    ticker (str): ticker of the stock to be added to the portfolio
		    shares (int): number of shares of the stock to be added to the portfolio
		
		Returns:
		    float: the difference in volatility of the portfolio if the specified number of shares of the ticker was added to the 
		    portfolio
		"""
		marginalPortfolio = self.basketPortfolio
		# If the stock is already in the portfolio, update the share count
		if ticker in marginalPortfolio: 
			marginalPortfolio[ticker] += shares
		# Otherwise add a new key/value pair to the dictionary with the new stock ticker and number of shares
		else:
			marginalPortfolio[ticker] = shares

		marginalSymbols = list(marginalPortfolio.keys())

		# Get the historical adjusted close stock prices for the stocks in the portfolio with the included stock and the number of shares
		marginalData = web.DataReader(marginalSymbols, "yahoo", self.startDate, self.endDate)['Adj Close']
		
		marginalData['Portfolio Value'] = None
		marginalData['Daily Returns'] = None
		totalValue = 0

		# Calculate daily portfolio value and daily returns
		for row in range(0, len(marginalData)): # iterate through rows
			for i in marginalPortfolio: # iterate through tickers
				totalValue += marginalData[i].iloc[row] * marginalPortfolio[i]
			marginalData['Portfolio Value'].iloc[row] = totalValue
			if row != 0:
				marginalData['Daily Returns'] = marginalData['Portfolio Value'].pct_change(1)
			totalValue = 0

		# Calculate standard deviation of the portfolio's daily returns with the included stock and the number of shares
		self.__marginalPortfolioVolatility = marginalData['Daily Returns'].std()
		return self.__marginalPortfolioVolatility - self.__portfolioVolatility

	def maxDrawDown(self):
		"""
		Returns:
		    float: maximum drawdown of the portfolio (largest drop from peak to trough in the lifespan of the portfolio)
		"""
		# Initialize values to 0
		peak = 0
		trough = 0
		DDCurrent = 0
		DDTotal = 0

		# Iterate through the daily portfolio values
		for value in self.priceData['Portfolio Value']:
			# If the current value is greater than the current peak, set the peak equal to the current value
			# Reset trough value
			# Reset current dropdown value
			if value > peak:
				peak = value
				trough = 0 
				DDCurrent = 0

			# If trough has not been initialized and the current value is less than the peak, set the trough equal to the current value
			elif value < peak and trough == 0:
				trough = value

			# If the current value is less than the trough, set the trough equal to the current value
			else:
				trough = value

			# When both the peak and trough are initialized, calculate current dropdown value
			if peak != 0 and trough != 0:
				DDCurrent = peak - trough

			# If the current dropdown value is greater than the previous dropdown value, update with the overall max dropdown value
			if DDCurrent > DDTotal:
				DDTotal = DDCurrent
		self.__maxDrawDownValue = DDTotal/peak
		return self.__maxDrawDownValue

basket = {"AAPL": 50, "GME": 150, "TSLA": 5, "AAL": 200, "AMZN": 1}
start = dt.date(2019, 1, 1)
end = dt.date(2021, 3, 1)
benchmark = "VOO"

portfolio = Portfolio(basket, start, end, benchmark)

print("Average Daily Return: " + str(round(portfolio.averageDailyReturn()*100, 3)) + "%")
print("Volatility: " + str(round(portfolio.volatility()*100, 3)) + "%")
print("Risk Ratio: " + str(round(portfolio.riskRatio(), 3)))
print("Marginal Volatility: " + str(round(portfolio.marginalVolatility("GME", 300)*100, 3)) + "%")
print("Max Draw Down: " + str(round(portfolio.maxDrawDown()*100, 3)) + "%")
