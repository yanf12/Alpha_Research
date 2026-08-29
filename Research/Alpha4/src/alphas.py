import warnings
import os

# 忽略所有警告
warnings.filterwarnings("ignore")

import pickle
from tqdm import tqdm
import importlib
import simres.expr
importlib.reload(simres.expr)
from simres.expr import *

enddate='20251231'

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
with open(os.path.join(script_dir, 'csi500.txt'), 'r') as f:
    alpha_list=f.read().split('\n')

executor = AlphaExecutor(data_dir=f'/Users/qiuyucheng/Documents/Alpha4/data/{enddate}')
executor.load_all_data()

for i in tqdm(range(len(alpha_list))):
    expr=alpha_list[i]
    alpha = executor.evaluate(f'at_nan2zero(cs_booksize(cs_rank(at_mask({expr},ts_fill(csi_500_weight)>0))-0.5))')
    # alpha返回的只是一个numpy数组; 必须用pandas给alpha再穿上index和columns!;
    pd.DataFrame(alpha,index=executor.context['stock_list'],columns=executor.context['datestr']).to_parquet(os.path.join(project_dir, f"alphas/{enddate}/matrix/"+str(5000001+i)))
    # btresult是回测结果,是一个字典形式的;
    #  return {       # 这是backtest返回的结果形式;
    #                     'datestr':self.context['datestr'],
    #                     'net_ret':net_daily,
    #                     'long_ret':long_daily,
    #                     'short_ret':short_daily,
    #                     'tvr':daily_tvr,
    #                     'long_num':long_num,
    #                     'short_num':short_num,
    #                    }
    btresult=executor.backtest(alpha)
    btresult['alpha_id']=str(5000001+i)
    with open(os.path.join(project_dir, f"alphas/{enddate}/simres/"+str(5000001+i)+".pkl"), "wb") as f:
        pickle.dump(btresult, f)