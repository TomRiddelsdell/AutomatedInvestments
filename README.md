# AutomatedInvestments

Further Development
    - Use clustering on distance matrix group clusters of similar tickers (for any given distance tolerance)
    - Measure the impact of distance tolerance on diversification
    - Merge time-series of the longest running ticker in the cluster to extend our potential backtest period
	- Retrieve fees for each ETF
	- Check return type of each ETF - could we be ignoring a dividend yield?
	- Optimize distance tolerance or at least display a price of diversification given the fees
	- Add support for backtesting the strategies
	- Incorporate transaction costs and display performance sensitivity to rebalancing/observation frequencies
	- Implement checks to ensure we're not including any splits or other corporate actions
	- Manage the FX risk:
	    - Convert all TSs to a base currency before optimization (not sure that makes sense for risk parity approach)
	    - Display currency weighting chart along with the optimized portfolio
	    - Use Black-Litterman approach to calculate optimal FX hedging
	- Implement correlation matrix filter and see if it effects the results: https://github.com/steve98654/PyTalk/blob/master/pydata_talk.ipynb
	- User Black-Litterman approach to combine multiple portfolios
	- Build portfolios optimized for other metrics (Value, Momentum, Low-Beta, Quality, Size, Trend) - Maybe we can just abstract the mean-variance optimizer?
