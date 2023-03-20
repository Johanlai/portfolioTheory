# portfolioTheory

- Retreived data of each of the FTSE100 constituents 
- Assessed the parameters to best optimise the portfolio, including reset frequencies, window size)
- Visualise the differences between the portfolios generated
- Used the output parameters to build an application to automate the process

# Summary

results show that using as much data as possible is the most effective.
 

Portfolio optimisation
There are 21 years in the dataset and an average of 237 days per year.
![average_days_per_year](https://user-images.githubusercontent.com/65450101/222821097-996b088a-305a-495a-ac4a-000350c51e13.png)<br>
The prices display exponential growth over time.
![image](https://user-images.githubusercontent.com/65450101/222821205-32742b6c-cbc2-4c3b-b460-48447e8087c1.png)

![image](https://user-images.githubusercontent.com/65450101/222821467-1d3bc7d4-5d6b-4b53-8e0c-d5018535aec2.png)

![image](https://user-images.githubusercontent.com/65450101/222821472-bb5c3d7b-fd5d-4bae-a7cb-5f32cdda5780.png)

![perc_vs_log_return](https://user-images.githubusercontent.com/65450101/222821788-5ff89af6-4b37-49b9-b7a2-5e8aad343167.png)

![QQ plot](https://github.com/Johanlai/portfolioTheory/blob/main/Media/QQ%20plot.png)

## Stuff to try next time
- Ledoit and Wolf single factor matrix of sharpe
- CLA
- LSTM

# to clean 

### Out of sample window
The out of sample window used a static window of historical data to set the 
optimal weights for the next period. Using intevals 3, 6 and 12 months, the 
reulsts show that the annual (12 month) reset performed the best by a
subtantial margin.

This is likey because the data in the other windows were too sparse to
accurately model the mean-variance of the portfolio.

### Cumulative sample
The cumulative sample used all available historical data to set the optimal
weights for the following period, and was tested at the same reset intervals
(3, 6, 12 months). In this test, the differences were negligble and supports
the idea that the out-of-sample window underperformed due to insufficient data.