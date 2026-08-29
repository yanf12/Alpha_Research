# Alpha Expressions

The expressions below are sourced from `Alpha4/src/csi500.txt`. They are listed in execution order and map to alpha IDs `5000001` through `5000120`.

```text
ts_mean(vwap-close,5)
-ts_correlation(close, volume, 5)
cs_rank(cs_rank(open)-cs_rank(ts_delay(close,1)))
ts_correlation(ts_ret(low,1),ret1,3)
ts_ols(open/ts_delay(close,1),ts_delay(volume,1),10)[2]
-ts_ols(close,ret1,10)[2]
-ts_correlation(close,close/low-1,15)
-ts_correlation(close,np.abs(ret1),5)
-ts_correlation(close,close/vwap-1,20)
ts_correlation(cs_rank(ts_delay(volume,1)),cs_rank(ret1),5)
-close*volume*ts_zscore(ret1,2)
ts_correlation(ret1,csi_500_ret1,20)
ts_ols(ret1,ts_delay(csi_500_ret1,1),5)[0]
ts_ols(ret1,ts_delay(ret1,1),20)[0]
-ts_ols(ret1,ts_delay(ret1,1),20)[2]
-ts_ols(ret1,volume,10)[0]
-ts_ols(cs_rank(high),cs_rank(low),10)[2]
-ts_ols(cs_rank(high),cs_rank(open),20)[2]
cs_indneut(high-close,cs_group_quantile(at_mask(close,ts_fill(csi_500_weight)>0),10))
ts_mean(at_mask(vwap-close,cs_rank(at_mask(volume,ts_fill(csi_500_weight)>0))>0.5),2)
-ts_skewness(close,20)
ts_skewness(vwap-close,10)
ts_kurtosis(ts_delta(close,1),20)
ts_std(low/ts_delay(close,1)-1,100)-ts_std(high/ts_delay(close,1)-1,100)
cs_indneut(ts_mean(open-close,2),cs_group_quantile(at_mask(ts_std(close,2),ts_fill(csi_500_weight)>0),50))
ts_ols(csi_500_ret1,ret1,5)[0]
-ts_regression(csi_500_ret1,ts_delay(ret1,1),50,0)
-ts_regression(csi_500_ret1,amount,30,0)
-ts_ols(ret1-csi_500_ret1,ret1,5)[0]
-ts_ols(ts_rank(close,10),ts_rank(np.abs(ret1),10),10)[0]
-ts_ols(ts_rank(close,3),ts_rank(vwap,3),3)[2]
-ts_regression(ts_rank(close,10),ts_rank(ret1,10),10,5)
-ts_regression(csi_500_open/ts_delay(csi_500_close,1),close/ts_delay(close,1),10,4)
ts_ols(ts_skewness(ret1,5),ret1,5)[0]
-ts_regression(ts_skewness(ret1,3),ret1,7,9)
-ts_correlation(cs_rank(ts_delta(volume,1)),cs_rank(ts_delta(close,1)),10)
-ts_ols(ret1, csi_500_ret1,5)[1]
at_mask(ts_correlation(ts_rank(amount/csi_500_amount, 5), csi_500_ret1, 15), ts_fill(csi_500_weight)>0)
ts_regression(ts_skewness(volume, 10), ts_kurtosis(volume, 10), 20, 0)
cs_indneut(ts_mean(high/close-1,5), cs_group_quantile(at_mask(ts_std(volume,10),ts_fill(csi_500_weight)>0), 10))
ts_regression(ts_rank(volume, 5), ts_rank(high/low-1, 10), 20, 6)
-cs_indneut(ts_zscore(ts_skewness(close/vwap-1, 10), 5), cs_group_quantile(at_mask(ts_rank(volume, 5), ts_fill(csi_500_weight)>0), 10))
cs_indneut(ts_mean(ts_rank(open-close, 10), 5), cs_group_quantile(at_mask(ts_kurtosis(ret1, 20), ts_fill(csi_500_weight)>0), 10))
-ts_mean(close/low-1, 5)
-ts_correlation(amount/csi_500_amount, ret1, 5)
ts_correlation(vwap-close, csi_500_vwap-csi_500_close, 5)
-ts_ols(ret1, csi_500_vwap_ret1, 30)[1]
ts_correlation(high/low-1, csi_500_high/csi_500_low-1, 4)
ts_ols(high/close-1, csi_500_ret1, 10)[2]
ts_zscore(high-close, 5)
ts_ols(low/ts_delay(close,1)-1, csi_500_low/ts_delay(csi_500_close,1)-1, 5)[1]
ts_ols(vwap / close - 1, csi_500_vwap / csi_500_close - 1, 5)[1]
ts_correlation(high/low-1, csi_500_high/csi_500_low-1, 10)
-cs_rank(ts_correlation(volume/csi_500_volume, close, 20))
at_mask(ts_zscore(volume/csi_500_volume, 10), ts_fill(csi_500_weight)>0)
-ts_correlation(high-low, amount, 15)
-ts_mean(ts_ols(high, low, 5)[2] * (close - vwap), 10)
ts_ols(vwap-close, volume, 5)[2]
at_mask(ts_correlation(close, csi_500_close, 5), ts_fill(csi_500_weight) > 0)
-ts_mean(amount/csi_500_amount - ts_delay(amount/csi_500_amount, 1), 5)
ts_ols(ret1, csi_500_ret1, 5)[0]
ts_correlation(high/close-1, csi_500_high/csi_500_close-1,5)
-ts_ols(close/vwap-1, csi_500_close/csi_500_vwap-1, 4)[2]
-ts_correlation(ts_ols(close, vwap, 20)[2], ts_delay(ts_ols(close, vwap, 20)[1], 1), 5)
-cs_rank(ts_skewness(amount, 20))
ts_ols(volume/csi_500_volume, csi_500_ret1, 5)[0]
-cs_indneut(ts_mean(close/vwap-1,20), cs_group_quantile(at_mask(volume, ts_fill(csi_500_weight)>0),20))
-ts_ols(high/low-1, csi_500_high/csi_500_low-1, 3)[1]
-ts_mean(ts_delta(vwap/csi_500_vwap, 1), 5)
-cs_indneut(ts_mean(high-vwap, 4), cs_group_quantile(at_mask(volume, ts_fill(csi_500_weight)>0), 2))
-ts_ols(vwap/low-1, csi_500_high/csi_500_low-1, 5)[1]
at_mask(ts_correlation(close/vwap-1, csi_500_ret1, 4), ts_fill(csi_500_weight)>0)
ts_mean(cs_rank(ts_correlation(close, vwap, 4)), 15)
ts_ols(vwap-close, csi_500_close-csi_500_vwap, 5)[2]
ts_mean((vwap-close)/(high-low), 2)
-ts_ols((close/vwap)-1, (high/low)-1, 3)[2]
ts_ols(low/close-1, csi_500_low/csi_500_close-1, 4)[1]
ts_correlation(cs_rank(volume/csi_500_volume), ts_zscore(high/close-1, 5), 10)
ts_ols(ret1, vwap-close, 10)[2]
ts_ols(cs_rank(ts_zscore(vwap-close,3)),cs_rank(ts_zscore(high-low,3)),10)[2]
ts_ols(ret1-csi_500_ret1,volume/csi_500_volume,4)[1]
ts_ols(ts_rank(close, 5), ts_rank(csi_500_close, 5), 10)[0]
ts_zscore(ts_ols(low/close-1, csi_500_ret1, 15)[2], 20)
-ts_zscore(amount * (close - vwap),4)
ts_ols(ts_zscore(high-close,20), ts_zscore(csi_500_high-csi_500_close, 10),10)[2]
-ts_correlation(ts_rank(high,10), cs_rank(amount),2)
-ts_ols(close/vwap, csi_500_open/csi_500_close,30)[2]
-ts_ols(high/vwap-1, csi_500_high/csi_500_low-1,10)[1]
cs_rank(ts_ols(high/close-1, csi_500_high/csi_500_close-1,3)[2])
ts_correlation(ts_rank(low,5), ts_rank(close,5),15)
ts_correlation((close-low)/(high-low), (csi_500_close-csi_500_low)/(csi_500_high-csi_500_low),3)
-ts_mean(ts_delta(ts_ols(close, vwap,20)[2],5),10)
ts_ols(at_mask(high/low-1, ts_fill(csi_500_weight)>0), at_mask(amount, ts_fill(csi_500_weight)>0),5)[0]
ts_mean(cs_rank(high / close - 1) - cs_rank(csi_500_high / csi_500_close - 1),5)
cs_rank(ts_zscore(at_mask(high / close - 1, ts_fill(csi_500_weight) > 0), 20))
ts_mean(at_mask(open/ts_delay(close,1) - 1, ts_fill(csi_500_weight) > 0),2)
ts_correlation(amount, vwap-close,10)
ts_mean(ts_ols(ts_skewness(high/low-1, 10), ts_skewness(csi_500_high/csi_500_low-1, 10), 20)[0],5)
ts_mean(at_mask(cs_rank(vwap/ts_delay(close,1)-1)-cs_rank(close/ts_delay(close,1)-1), ts_fill(csi_500_weight)>0),4)
-cs_indneut(ts_mean(volume/csi_500_volume,4), cs_group_quantile(at_mask(ts_std(close,3), ts_fill(csi_500_weight) > 0),3))
ts_ols(vwap-close, csi_500_vwap-csi_500_close,3)[1]
-ts_mean(ts_zscore(ts_delta(close/vwap-1, 1), 10), 10)
cs_rank(ts_mean(at_mask(vwap-close, ts_rank(volume, 10) > 0.5), 5))
-ts_ols(ts_rank(volume,5), ts_rank(csi_500_volume,5), 5)[1]
-cs_rank(ts_correlation(ts_mean(vwap, 10), ts_mean(volume, 5), 5))
-ts_ols(ts_std(high/close-1, 5), ts_std(csi_500_high/csi_500_close-1, 5),3)[1]
cs_rank(ts_mean(at_signed_power(ts_delta(vwap/close-1, 1), 0.2), 10))
-cs_zscore(ts_ols(ret1 - csi_500_ret1, ts_delay(volume/csi_500_volume, 1),3)[1])
ts_mean(cs_indneut(ts_argmax(volume/csi_500_volume, 10), cs_group_quantile(ts_std(close, 20),10)),4)
ts_mean(cs_zscore(ts_regression(close, vwap,10, 0)),2)
ts_mean(ts_correlation(ts_skewness(ret1, 10), csi_500_ret1, 15), 5)
ts_mean(ts_rank(high/close-1,5),10)
ts_delta(ts_mean(open-close,5),3)
ts_mean(at_condition(ts_rank(volume,5)>0.5,vwap-close,0),10)
ts_mean(at_condition(ts_rank(volume/csi_500_volume,3)>0.5,high/close-1,low/close-1),10)
cs_rank(at_condition(ts_rank(volume/csi_500_volume,5)>0.5,ts_mean(high/close-1,5),ts_mean(low/close-1,5)))
ts_mean(cs_mad(ts_skewness(vwap-close,20),3),5)
ts_mean(cs_rank(ts_ols(high-close,csi_500_high-csi_500_close,5)[2]),5)
ts_ols(at_condition(ts_rank(volume/csi_500_volume,3)>0.5,high/close-1,low/close-1),csi_500_ret1,5)[2]
cs_rank(ts_mean(at_mask(ts_ols(vwap-close,volume,5)[2],ts_fill(csi_500_weight)>0),10))
```