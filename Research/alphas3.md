# Alpha Factors 3 / Alpha 因子 3

This document records the following fundamental and price-volume factors in Chinese and English.

## Fundamental Factors / 基本面因子

1. **Receivables growth adjusted by cash-collection growth / 现金回款增长调整后的应收款增长**

   Chinese: `(当前季度应收款 - 去年同期应收款) * 正常增长乘数 / 当前季末总资产 * -1`，其中应收款 = 应收账款 + 预付账款；正常增长乘数 = 最新季度销售商品、提供劳务收到的现金 / 去年同季度销售商品、提供劳务收到的现金。

   English: `-(current-quarter receivables - receivables in the same quarter last year) * normal-growth multiplier / total assets at the current quarter-end`, where receivables = accounts receivable + prepayments, and the normal-growth multiplier = cash received from sales of goods and services in the latest quarter / cash received from sales of goods and services in the same quarter last year.

2. **Cumulative profit surprise relative to earnings guidance / 累积净利润相对业绩预告偏离度**

   Chinese: `(实际累积净利润 - (业绩预告上限 - 业绩预告下限) / 2) / 实际单季度净利润`。

   English: `(actual cumulative net profit - (upper bound of earnings guidance - lower bound of earnings guidance) / 2) / actual single-quarter net profit`.

3. **TTM operating-profit growth / 营业利润 TTM 同比增长率**

   Chinese: `(营业利润 TTM - 去年同期营业利润 TTM) / 去年同期营业利润 TTM`。

   English: `(trailing-twelve-month operating profit - trailing-twelve-month operating profit in the same period last year) / trailing-twelve-month operating profit in the same period last year`.

4. **Single-quarter gross-margin growth / 单季度毛利率同比增长率**

   Chinese: `(最近报告期单季度毛利率 - 上年同期单季度毛利率) / abs(上年同期单季度毛利率)`。

   English: `(single-quarter gross margin in the most recent reporting period - single-quarter gross margin in the same period last year) / abs(single-quarter gross margin in the same period last year)`.

5. **Shareholder-count percentile over five years / 股东户数过去五年分位数**

   Chinese: 股东户数在过去 5 年的分位数。

   English: Percentile rank of the shareholder count over the past five years.

6. **Volatility of equity-to-fixed-assets ratio growth / 股东权益与固定资产比率增长率波动率**

   Chinese: 过去 $N$ 个季度股东权益与固定资产比率增长率的波动率，$N = 8, 16, 48$。

   English: Volatility of the growth rate of the shareholders' equity-to-fixed-assets ratio over the past $N$ quarters, with $N = 8, 16, 48$.

7. **Operating cash flow to total liabilities / 经营活动现金流与负债比率**

   Chinese: `经营活动产生的现金流量净额 / 负债合计`。

   English: `net cash flow from operating activities / total liabilities`.

## Price-Volume Factors / 量价因子

1. **One-month return excluding limit-up days / 剔除涨停日的过去一个月收益率**

   Chinese: 过去一个月的收益率，剔除区间内所有触及涨停交易日的收益率。

   English: Return over the past month after excluding the returns of all trading days that touched the upper price limit during the period.

2. **Mean Williams lower shadow / 威廉下影线均值**

   Chinese: 威廉下影线在过去 $N$ 个交易日的均值，其中威廉下影线 = `(收盘价 - 最低价) / 最低价`。

   English: Mean Williams lower shadow over the past $N$ trading days, where the Williams lower shadow = `(close - low) / low`.

3. **Average return-to-turnover on positive-return days / 正收益日收益率与成交额比值均值**

   Chinese: 过去 $N$ 个交易日中，收益率为正的交易日的 `(日收益率 / 日成交额)` 平均值，$N = 20, 40, 60, 120$。

   English: Average `(daily return / daily turnover)` across positive-return trading days during the past $N$ trading days, with $N = 20, 40, 60, 120$.