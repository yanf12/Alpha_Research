#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试因子库中所有因子的 IC 和 IC 衰减
"""
import sys
import os
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
import pandas as pd
from tqdm import tqdm
from src.simres.expr import AlphaExecutor

def batch_test_ic():
    enddate = '20251231'
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 初始化执行器
    executor = AlphaExecutor(data_dir=f'{project_dir}/data/{enddate}')
    executor.load_all_data()
    
    # 读取因子列表
    with open(f'{project_dir}/src/csi500.txt', 'r') as f:
        alpha_list = [line.strip() for line in f.read().split('\n') if line.strip()]
    
    print(f"已加载 {len(alpha_list)} 个因子")
    
    # 存储结果
    results = []
    
    for i in tqdm(range(len(alpha_list)), desc="测试"):
        expr = alpha_list[i]
        alpha_id = str(5000001 + i)
        
        try:
            final_formula = f'at_nan2zero(cs_booksize(cs_rank(at_mask({expr},ts_fill(csi_500_weight)>0))-0.5))'
            alpha = executor.evaluate(final_formula)
            
            if alpha is not None:
                # 计算 IC 及衰减
                ic_result = executor.compute_ic(alpha)
                decay = executor.compute_ic_decay(alpha, max_lag=10)
                
                # 回测
                bt_result = executor.backtest(alpha)
                cut_result = executor.simres_cut(bt_result, '20150101', '20251231', if_plot=False)
                
                results.append({
                    'alpha_id': alpha_id,
                    'expr': expr,
                    'ic': ic_result['ic'],
                    'rank_ic': ic_result['rank_ic'],
                    **{f'ic_lag{k}': decay[k]['ic'] for k in range(1, 11)},
                    **{f'rank_ic_lag{k}': decay[k]['rank_ic'] for k in range(1, 11)},
                    'sr': cut_result['sr'],
                    'ann_ret': cut_result['ann_ret'],
                    'dd': cut_result['dd'],
                    'tvr_avg': cut_result['tvr_avg']
                })
        except:
            continue
    
    # 保存结果
    results_df = pd.DataFrame(results)
    results_df['abs_ic'] = results_df['ic'].abs()
    results_df = results_df.sort_values('abs_ic', ascending=False)
    results_df.to_csv(f'{project_dir}/ic_test_results.csv', index=False, encoding='utf-8-sig')
    
    # ========== 输出 SR > 2 的所有因子 ==========
    sr_good = results_df[results_df['sr'] > 2].sort_values('sr', ascending=False)
    
    print(f"\n{'='*80}")
    print(f"SR > 2 的因子 ({len(sr_good)} 个)")
    print(f"{'='*80}")
    
    for _, row in sr_good.iterrows():
        print(f"\n因子 {row['alpha_id']} | SR={row['sr']:.3f} | IC={row['ic']:.4f} | Rank_IC={row['rank_ic']:.4f}")
        print(f"表达式: {row['expr']}")
        print(f"年化收益={row['ann_ret']:.3f} | 最大回撤={row['dd']:.1f}% | 换手={row['tvr_avg']:.3f}")
        print("IC衰减: ", end="")
        for k in range(1, 11):
            print(f"{row[f'ic_lag{k}']:+.4f}", end=" ")
        print()
        print("RankIC衰减: ", end="")
        for k in range(1, 11):
            print(f"{row[f'rank_ic_lag{k}']:+.4f}", end=" ")
        print()
        print("-" * 80)
    
    return results_df

if __name__ == "__main__":
    batch_test_ic()
