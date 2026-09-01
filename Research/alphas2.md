# Alpha Factors 2

Source: `spec10.xlsx`, worksheet `因子信息汇总`.

## Alpha 1

```text
-18*divide(sharesout,volume)-0.3*divide(rank(vwap^(1/3)),rank(low^(1/3)))+0.1*ts_regression(open,high,21,lag = 0, rettype = 2)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 32 |
| Delay | 1 |
| Truncation | 0.08 |
| Neutralization | Market |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 2

```text
ts_decay_linear(rank(vec_sum(fnd6_newqeventv110_glaq)), 10) - ts_decay_linear(rank(vec_sum(fnd6_newqeventv110_glaq)), 60)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 430 |
| Delay | 1 |
| Truncation | 0.03 |
| Neutralization | None |
| Pasteurization | Off |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 3

```text
ts_mean(2.4 *ts_rank(operating_income / close, 126)-1.4* ts_rank(close / ts_delay(close, 21),63)-0.4 * ts_rank(volume / adv20,126)-0.2 *(ts_rank(income / equity,63)),30)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP500 |
| Language | Fast Expression |
| Decay | 1 |
| Delay | 1 |
| Truncation | 0.08 |
| Neutralization | None |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 4

```text
-ts_backfill(if_else(rel_num_all,-0.5,news_max_dn_ret),60)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 4 |
| Delay | 0 |
| Truncation | 0.2 |
| Neutralization | Market |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 5

```text
group_neutralize(-ts_product(winsorize(ts_backfill(vec_avg(anl4_fsdetailrecv4v104_item), 120), std=4), 240),densify(bucket(rank(cap), range='0.1, 1, 0.1')))
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 6 |
| Delay | 1 |
| Truncation | 0.08 |
| Neutralization | Subindustry |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 6

```text
reverse(days_from_last_change(vec_avg(fnd6_stype)))
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 5 |
| Delay | 1 |
| Truncation | 0.05 |
| Neutralization | Subindustry |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 7

```text
scale(group_neutralize(signed_power(0.01, 2), densify(pv13_hierarchy_min2_focused_pureplay_3000_513_sector)))
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 131 |
| Delay | 1 |
| Truncation | 0.02 |
| Neutralization | Market |
| Pasteurization | Off |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 8

```text
group_neutralize(ts_mean(winsorize(ts_backfill(anl4_ptp_flag, 120), std=4), 240),densify(bucket(rank(cap), range='0.1, 1, 0.1')))
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 5 |
| Delay | 1 |
| Truncation | 0.08 |
| Neutralization | Subindustry |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 9

```text
(((ts_sum(high,45)/40)< high)?(-1*ts_delta(high, 5)):0)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 29 |
| Delay | 1 |
| Truncation | 0.08 |
| Neutralization | Subindustry |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |

## Alpha 10

```text
amihud = (10^6)*(1/252)*ts_sum(abs(returns)/volume,252);
illiquidity = normalize(amihud,useStd=false);
-hump(group_neutralize(ts_corr(illiquidity,amihud,42),bucket(rank(mdl177_valuemomemtummodel_reportedearningsmomentummodule),range="0.4,1,0.2")),hump=0.0005)
```

| Setting | Value |
| --- | --- |
| Instrument Type | Equity |
| Region | USA |
| Universe | TOP3000 |
| Language | Fast Expression |
| Decay | 0 |
| Delay | 1 |
| Truncation | 0.03 |
| Neutralization | Subindustry |
| Pasteurization | On |
| Max Trade | OFF |
| Max Position | OFF |