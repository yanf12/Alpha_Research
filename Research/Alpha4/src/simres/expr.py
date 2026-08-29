import os
import sys
import inspect
import pickle
import traceback
import numpy as np
import pandas as pd
import bottleneck as bn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates




# --- 自动路径挂载 ---
try:
    curr_path = os.path.dirname(os.path.abspath(__file__))
except NameError:
    curr_path = os.getcwd()

if curr_path not in sys.path:
    sys.path.insert(0, curr_path)

# 尝试导入你的算子库
try:
    import operators as op
except ImportError:
    print("警告: 未找到 op 模块，请确保目录结构正确。")
    op = None

class AlphaExecutor:
    def __init__(self, data_dir,alpha_dir=None):
        self.data_dir = data_dir  # 股票文件的目录路径
        self.alpha_dir = alpha_dir # alpha文件的目录路径，当跑完alpha.py之后，算出来的矩阵matrix和simres；
        # 上下文环境存放的字典，在内存中全量存放股票的行情矩阵和计算结果；
        # 执行完load_all_data后，context中存放：{'close':np.ndarray,'vwap':np.ndarray,...},每一个value都是(1326,2674)的numpy矩阵;
        # 当我们在evaluate函数中,eval(expression, ..., self.context) 去解析expression的时候，会把context当成变量传进去d
        # python会自动去self.context字典里抓取名为vwap和close的numpy矩阵进行计算;
        self.context = {}
        self.alpha_pool=[] # 装alpha因子的回测数据字典（simres_result），里面装的都是每个因子的回测结果；
        self.alpha_matrix=[] #记录alpha的列表，里面存放的都是已经计算好得分的numpy矩阵(Stock,Date)——（1326，2674）
        self.data_loaded = False

    #    将simres（36个因子回测文件全部载入alpha_pool）
    # self.alpha_pool = [
    #     {
    #         'alpha_id': '5000001',
    #         'net_ret': np.array([...]), # 该因子的每日收益率序列
    #         'tvr': np.array([...]),     # 该因子的每日换手率序列
    #         'sr': 1.45                  # 夏普比率
    #         '...':
    #     },
    #     {
    #         'alpha_id': '5000002',
    #         'net_ret': np.array([...]),
    #         ...
    #     }
    # ]
    def load_all_simres(self):
        if not os.path.exists(self.alpha_dir):
            raise FileNotFoundError(f"Alpha目录 {self.alpha_dir} 不存在")
        print(f"--- 正在初始化数据引擎 ---")
        # 按文件名排序，确保加载顺序一致
        files = sorted(os.listdir(os.path.join(self.alpha_dir,'simres')))
        for file in files:
            file_path = os.path.join(self.alpha_dir,'simres', file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue
            name = os.path.splitext(file)[0] # 比如说：5000001.pkl 提取出来5000001；
            try:
                with open(file_path, "rb") as f:
                    # 用 pickle 把硬盘里的二进制账本读成 Python 字典
                    # 在运行alphas.py的时候用pickle.dump把因子的收益率、换手率、等字典结构压成了二进制文件，这里把他们解冻；
                    simres_result = pickle.load(f)
                if 'alpha_id' not in simres_result:
                    simres_result['alpha_id']=name  # 如果账本里没写名字，用文件名当名字
                self.alpha_pool.append(simres_result)  #将simres_result塞入alpha_pool
                # 在机器学习的多因子合成中，横向对比哪个因子收益高、回撤小。
                print('success load alpha simres'+name)
            except:
                print('fail to load alpha simres'+name)

    # 把所有计算好的因子矩阵文件（Parquet 格式）挨个读进内存，转成纯粹的 NumPy 二维矩阵 (1326, 2674)，
    # 然后整整齐齐地追加（append）到 self.alpha_matrix 列表中 。
    #
    def load_all_alphas(self):
        if not os.path.exists(self.alpha_dir):
            raise FileNotFoundError(f"Alpha目录 {self.alpha_dir} 不存在")

        print(f"--- 正在初始化数据引擎 ---")
        # 按文件名排序，确保加载顺序一致
        files = sorted(os.listdir(os.path.join(self.alpha_dir,'matrix')))
        for file in files:
            file_path = os.path.join(self.alpha_dir,'matrix', file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue
            name = os.path.splitext(file)[0] # 依旧从5000001.parquet获取5000001
            try: #读入parquet文件，用values拿掉pandas索引的外壳，转为纯数字的numpy 1326 x 2674矩阵
                matrix=pd.read_parquet(file_path).values.astype(np.float32)
                # 将所有alpha的矩阵加入 alpha_matrix
                # 这个在机器学习中的多因子合成中，可以作为原始特征输入
                self.alpha_matrix.append(matrix)
                print('success load alpha matrix'+name)
            except:
                print('fail to load alpha matrix'+name)

    #   检查因子间相关性：这个检查的逻辑是按照 net_ret 去进行检查的,检查收益率的相关性
    def corr(self,simres):
        # copy36个因子的回测结果
        alpha_pool=self.alpha_pool.copy()
        # simres就是我们这个需要去对比相关性的这个新因子，加入到alpha_pool
        alpha_pool.append(simres)
        # 对于alpha_pool中的每一个字典item,将所有item的每天的每日多空净收益率序列提取出来;
        # 用corrcoef计算二维的相关性系数矩阵,并将最后以后提取出来
        corr_matrix=np.corrcoef([item['net_ret'] for item in alpha_pool])[-1]
        result_pool=[]
        for i in range(len(alpha_pool)-1):
            start_date=alpha_pool[i]['datestr'][0]
            end_date=alpha_pool[i]['datestr'][-1]
            # 对老因子的表现重新做了一次指标切片计算
            simres_result=self.simres_cut(alpha_pool[i], start_date, end_date,if_plot=False)
            # 关键动作：把刚刚算出来的相关系数，强行注入到该因子的评级指标里！
            simres_result['corr']=corr_matrix[i]
            simres_result['alpha_id']=alpha_pool[i]['alpha_id']
            result_pool.append(simres_result)
        #     按照相关系数从大到小（降序）排序，并用 .iloc[:5] 打印出和新因子长得最像的前 5 个老因子。
        print(pd.DataFrame(result_pool).sort_values('corr',ascending=False).iloc[:5])
        return result_pool


    # 加载data目录下面的原始数据;
    def load_all_data(self):
        """
        一键载入 data 文件夹下的所有文件 (csv/parquet)
        自动将 DataFrame 转为 (Stock, Date) 的 float32 矩阵
        """
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"数据目录 {self.data_dir} 不存在")

        print(f"--- 正在初始化数据引擎 ---")
        for file in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue

            name = os.path.splitext(file)[0]
            if name=='pv':
                continue
            try:
                
                df = pd.read_parquet(file_path, engine='pyarrow')
                
                # 统一转为 float32 以节省内存，形状保持 (Stock, Date)
                if name in {'datestr','stock_list'}:
                    # 如果是 日期 和 股票名，直接剥离成一个简单干净的一维数组（Vector）
                    self.context[name] = df.values.reshape(-1)
                else:
                    # 如果是普通的量价数据,直接用.values暴力撕掉Pandas的外壳，只留下底层最纯粹的数字（1326 x 2674的numpy二维矩阵）
                    self.context[name] = df.values.astype(np.float32)
                print(f"已加载字段: [{name}] | 形状: {self.context[name].shape}")
            except Exception:
                print(f"载入 {file} 失败")
                traceback.print_exc()
        
        self.context['csi_500_vwap']=self.context['csi_500_amount']/self.context['csi_500_volume']*10
        self.context['vwap']=self.context['amount']/self.context['volume']*10
        self.context['ret1']=op.ts_ret(self.context['close'],1)
        self.context['csi_500_ret1']=op.ts_ret(self.context['csi_500_close'],1)
        self.context['csi_500_vwap_ret1']=op.ts_ret(self.context['csi_500_vwap'],1)

        
        # 注入 NumPy 命名空间
        self.context['np'] = np
        self.context['bn'] = bn
        self.context.update({n: getattr(np, n) for n in dir(np) if not n.startswith('_')})
        
        # 语义化轴定义
        self.context['CS'] = 0 # 截面轴 截面操作就传CS，时序操作就传TS
        self.context['TS'] = 1 # 时序轴

        # 一键注入自定义算子
        if op:
            # 过滤掉以 ‘_' 开头的算子’
            # k是算子名；v是本体作为value
            custom_ops = {k: v for k, v in inspect.getmembers(op, inspect.isfunction) 
                         if not k.startswith('_')}
            self.context.update(custom_ops)
            print(f"已注入自定义算子: {list(custom_ops.keys())}")

        self.data_loaded = True
        print(f"--- 引擎就绪 ---\n")



    # 将你写好的因子公式文本，瞬间翻译成底层由 NumPy 矩阵并行驱动的真实因子结果。
    def evaluate(self, expression):
        """
        执行表达式计算
        """
        if not self.data_loaded:
            self.load_all_data()

        try:
            # 限制执行环境，防止恶意调用
            # expression是因子文本，self.context是装有close、vwap矩阵、以及ts_mean等算子函数;
            result = eval(expression, {"__builtins__": None}, self.context)
            return result
        except Exception:
            print(f"表达式执行错误: {expression}")
            traceback.print_exc()
            return None


    # 模拟你在实盘中同时买入因子得分最高的股票（多头 Long），卖空因子得分最低的股票（空头 Short），
    # 并帮你计算出这条因子流水线在历史上每天真正的纯净对冲收益流、调仓换手率以及组合持仓状态。
    def backtest(self,alpha,price='vwap'):
        """
        基于 VWAP-to-VWAP 的回测与可视化
        :param alpha: np.ndarray (Stock, Date), 因子原始值
        :param vwap: np.ndarray (Stock, Date), VWAP价格
        :param dates: pd.DatetimeIndex, 对应 Date 维度
        """
        try:
            # 1. 计算收益率矩阵 (t+1 VWAP / t VWAP - 1)
            # 结果形状 (Stock, Date-1)
            vwap=self.context[price]  #在context中获取vwap价格
            dates = pd.to_datetime(self.context['datestr'])  #获取日期
            # 如果后续的回测需要更换 回测的目标：
            # 原来是1天收益   asset_ret = op.ts_ret(vwap,1)   weights = op.ts_delay(alpha, 2)
            # 现更换为2天收益  asset_ret = op.ts_ret(vwap, 2)   weights = op.ts_delay(alpha, 3)，延迟三天；
            asset_ret = op.ts_ret(vwap,1)   #用vwap价格获取收益率(1天的涨跌幅)
            
            # 2. 因子处理：截面归一化 (Booksize 逻辑)
            # 假设原始因子越大越看多
            # ts_delay(alpha, 2) —————— 表示第 t 日的权重 = 第t-2日的原始因子值
            # T日盘后计算出原始因子值
            # T+1全天不可能开盘价成交(我们用VWAP做价格),回测通常保守假设T+1日盘后才知道T+1日的VWAP,真正下单是T+2日盘初;
            # 但是我们的asset_ret用的 t—1 ——> t日的收益
            # 因此，映射关系变成：
            # 因子计算日 ：T
            # 因子值用于：T+2
            # 对应的收益区间 T+1 ——> T+2
            weights = op.ts_delay(alpha,2) # t日权重对应 t->t+1 的收益

            pos_mask = np.where(weights > 0, weights, 0) # 剥离出做多的股票
            neg_mask = np.where(weights < 0, weights, 0) # 剥离出做空的股票
            
            # 归一化：多头和空头各自权重和为 1
            long_w = pos_mask / np.nansum(pos_mask, axis=0)
            short_w = neg_mask / np.abs(np.nansum(neg_mask, axis=0))

            # 矩阵点乘求每日组合收益
            daily_tvr=np.nansum(np.abs(op.ts_delta(long_w+short_w,1)),axis=0)/2
            # 统计多空两端各踩中多少只股票
            long_num=np.nansum(np.where(long_w>0,1,0),axis=0)
            # 对冲后的纯净收益
            short_num=np.nansum(np.where(short_w<0,1,0),axis=0)

            # 3. 计算三条曲线的每日收益
            # long_w * asset_ret 是多头持仓矩阵和收益率矩阵的元素对位相乘
            long_daily = np.nansum(long_w * asset_ret, axis=0)
            # short_w * asset_ret 是空头持仓矩阵和收益率矩阵的元素对位相乘
            short_daily = np.nansum(short_w * asset_ret, axis=0)
            # 最后的对冲收益
            net_daily = long_daily + short_daily # 对冲收益
            
            # # 4. 计算累计收益 (假设初始资金 10000)
            # scale = 10000
            # long_pnl = np.nancumsum(long_daily) * scale
            # short_pnl = np.nancumsum(short_daily) * scale
            # net_strategy = np.nancumsum(net_daily) * scale

            # # 对齐日期 (因为收益率少了一天)
            # plot_dates = dates
            
            # # 5. 计算量化指标 (用于 Title)
            # ann_ret = np.nanmean(net_daily) * 252
            # ann_vol = np.nanstd(net_daily) * np.sqrt(252)
            # sr = ann_ret / ann_vol if ann_vol != 0 else 0
            # dd = (np.maximum.accumulate(net_strategy) - net_strategy).max() / scale * 100 # 简单回撤%
            # tvr=np.nanmean(daily_tvr)

            
            # # 6. 绘图逻辑 (按你提供的样式)
            # fig, ax = plt.subplots(figsize=(8, 8))
            # fig.patch.set_linewidth(2)
            # fig.patch.set_edgecolor('black')
            # ax.set_facecolor('white')
            # ax.grid(True, which='both', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.5)
    
            # # 绘图
            # ax.plot(plot_dates, long_pnl, color='black', label='Long', linewidth=0.8, alpha=0.8)
            # ax.plot(plot_dates, short_pnl, color='green', label='Short', linewidth=0.8, alpha=0.8)
            # ax.plot(plot_dates, net_strategy, color='red', label='ls', linewidth=1.5, zorder=5)
    
            # # 格式化
            # ax.xaxis.set_major_locator(mdates.YearLocator())
            # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
            # plt.xticks(rotation=30, ha='right', fontsize=8)
            
            # # 动态生成 Header
            # header = (f"sr:{sr:.3f} ret:{ann_ret:.3f} tvr:{tvr:.3f} num:{int(np.nanmean(op.at_zero2nan(long_num)))}|{int(np.nanmean(op.at_zero2nan(short_num)))} dd:{dd:.1f}" f"({plot_dates[0].strftime('%Y%m%d')}-{plot_dates[-1].strftime('%Y%m%d')})")
            # plt.title(header, loc='left', fontsize=10, family='monospace', pad=15)
            
            # ax.set_ylabel('Thousand Currencies', fontsize=8)
            # ax.legend(loc='upper left', fontsize=7, frameon=True, edgecolor='lightgray')
            # ax.set_xlim(plot_dates[0], plot_dates[-1])
            
            # plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
            # plt.show()
            
            return {
                    'datestr':self.context['datestr'],
                    'net_ret':net_daily,
                    'long_ret':long_daily,
                    'short_ret':short_daily,
                    'tvr':daily_tvr,
                    'long_num':long_num,
                    'short_num':short_num,
                   } 
    
        except Exception:
            traceback.print_exc()
    # def simres_cut(self,res, start_date, end_date,if_plot=True,index=None,alpha_id=None,save_path=None):
    #     """
    #     对回测结果进行区间切片并重新绘图
    #     :param res: backtest 函数返回的 dict
    #     :param start_date: 起始日期 字符串 e.g. '20180101'
    #     :param end_date: 结束日期 字符串 e.g. '20191231'
    #     """
    #     try:
    #         if 'alpha_id' in res:
    #             alpha_id=res['alpha_id']
    #         # 1. 提取原始数据
    #         dates = pd.to_datetime(res['datestr'])
    #         net_daily = res['net_ret']
    #         long_daily = res['long_ret']
    #         short_daily = res['short_ret']
    #         daily_tvr = res['tvr']
    #         long_num = res['long_num']
    #         short_num = res['short_num']
    #         if index is not None:
    #             short_daily = self.context[index][0]
    #             net_daily = long_daily-short_daily
    #
    #
    #
    #         # 2. 构造切片掩码
    #         mask = (dates >= pd.to_datetime(start_date)) & (dates <= pd.to_datetime(end_date))
    #
    #         if not np.any(mask):
    #             print(f"Error: No data found between {start_date} and {end_date}")
    #             return
    #
    #         # 3. 切片数据
    #         cut_dates = dates[mask]
    #         cut_net = net_daily[mask]
    #         cut_long = long_daily[mask]
    #         cut_short = short_daily[mask]
    #         cut_tvr = daily_tvr[mask]
    #         cut_long_num = long_num[mask]
    #         cut_short_num = short_num[mask]
    #
    #         # 4. 重新计算区间累计收益与指标
    #         scale = 10000
    #         # 重新从 0 开始计算累计值
    #         long_pnl = np.nancumsum(cut_long) * scale
    #         short_pnl = np.nancumsum(cut_short) * scale
    #         net_strategy = np.nancumsum(cut_net) * scale
    #
    #         ann_ret = np.nanmean(cut_net) * 252
    #         ann_vol = np.nanstd(cut_net) * np.sqrt(252)
    #         sr = ann_ret / ann_vol if ann_vol != 0 else 0
    #         dd = (np.maximum.accumulate(net_strategy) - net_strategy).max() / scale * 100
    #         tvr_avg = np.nanmean(cut_tvr)
    #
    #         # 处理平均票数 (复用你 at_zero2nan 的逻辑)
    #         def at_zero2nan(x): return np.where(x == 0, np.nan, x)
    #         avg_l_num = int(np.nanmean(at_zero2nan(cut_long_num))) if np.any(cut_long_num) else 0
    #         avg_s_num = int(np.nanmean(at_zero2nan(cut_short_num))) if np.any(cut_short_num) else 0
    #         if if_plot:
    #             # 5. 绘图 (复用 backtest 样式)
    #             fig, ax = plt.subplots(figsize=(8, 8))
    #             fig.patch.set_linewidth(2)
    #             fig.patch.set_edgecolor('black')
    #             ax.set_facecolor('white')
    #             ax.grid(True, which='both', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.5)
    #
    #             ax.plot(cut_dates, long_pnl, color='black', label='Long', linewidth=0.8, alpha=0.8)
    #             ax.plot(cut_dates, short_pnl, color='green', label='Short', linewidth=0.8, alpha=0.8)
    #             ax.plot(cut_dates, net_strategy, color='red', label=('' if alpha_id==None else alpha_id), linewidth=1.5, zorder=5)
    #
    #             # 格式化
    #             ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    #             ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
    #             plt.xticks(rotation=30, ha='right', fontsize=8)
    #
    #             header = (f"sr:{sr:.3f} ret:{ann_ret:.3f} tvr:{tvr_avg:.3f} "
    #                       f"num:{avg_l_num}|{avg_s_num} dd:{dd:.1f} "
    #                       f"({cut_dates[0].strftime('%Y%m%d')}-{cut_dates[-1].strftime('%Y%m%d')})")
    #             plt.title(header, loc='left', fontsize=10, family='monospace', pad=15)
    #
    #             ax.set_ylabel('Thousand Currencies', fontsize=8)
    #             ax.legend(loc='upper left', fontsize=7, frameon=True, edgecolor='lightgray')
    #
    #             # --- 强制设置起始和结束日期刻度 ---
    #             # 选取 5-6 个均匀分布的中间点 + 明确的起点和终点
    #             num_ticks = 7
    #             if len(cut_dates) > num_ticks:
    #                 # 选取均匀分布的索引
    #                 idx = np.linspace(0, len(cut_dates) - 1, num_ticks).astype(int)
    #                 display_dates = cut_dates[idx]
    #             else:
    #                 display_dates = cut_dates
    #
    #             # 设置刻度位置和标签
    #             ax.set_xticks(display_dates)
    #             ax.set_xticklabels([d.strftime('%Y%m%d') for d in display_dates],
    #                                rotation=30, ha='right', fontsize=8)
    #
    #             # 确保 X 轴范围严格对齐
    #             ax.set_xlim(cut_dates[0], cut_dates[-1])
    #
    #
    #
    #
    #             plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    #             if save_path!=None:
    #                 plt.savefig(save_path)
    #             plt.show()
    #
    #         return {
    #             'ann_ret':ann_ret,
    #             'ann_vol':ann_vol,
    #             'sr':sr,
    #             'dd':dd,
    #             'tvr_avg':tvr_avg,
    #         }
    #
    #     except Exception:
    #         traceback.print_exc()
    def simres_cut(self,res, start_date, end_date,if_plot=True,index=None,alpha_id=None,save_path=None):
        """
        对回测结果进行区间切片并重新绘图
        :param res: backtest 函数返回的 dict
        :param start_date: 起始日期 字符串 e.g. '20180101'
        :param end_date: 结束日期 字符串 e.g. '20191231'
        """
        try:
            if 'alpha_id' in res:
                alpha_id = res['alpha_id']
            # 1. 提取原始数据
            dates = pd.to_datetime(res['datestr'])
            net_daily = res['net_ret']
            long_daily = res['long_ret']
            short_daily = res['short_ret']
            daily_tvr = res['tvr']
            long_num = res['long_num']
            short_num = res['short_num']
            if index is not None:
                short_daily = self.context[index][0]
                net_daily = long_daily - short_daily

            # 2. 构造切片掩码
            mask = (dates >= pd.to_datetime(start_date)) & (dates <= pd.to_datetime(end_date))

            if not np.any(mask):
                print(f"Error: No data found between {start_date} and {end_date}")
                return

            # 3. 切片数据
            cut_dates = dates[mask]
            cut_net = net_daily[mask]
            cut_long = long_daily[mask]
            cut_short = short_daily[mask]
            cut_tvr = daily_tvr[mask]
            cut_long_num = long_num[mask]
            cut_short_num = short_num[mask]

            # 4. 重新计算区间累计收益与指标
            scale = 10000
            # 重新从 0 开始计算累计值
            long_pnl = np.nancumsum(cut_long) * scale
            short_pnl = np.nancumsum(cut_short) * scale
            net_strategy = np.nancumsum(cut_net) * scale

            ann_ret = np.nanmean(cut_net) * 252
            ann_vol = np.nanstd(cut_net) * np.sqrt(252)
            sr = ann_ret / ann_vol if ann_vol != 0 else 0
            dd = (np.maximum.accumulate(net_strategy) - net_strategy).max() / scale * 100
            tvr_avg = np.nanmean(cut_tvr)

            # 处理平均票数 (复用你 at_zero2nan 的逻辑)
            def at_zero2nan(x):
                return np.where(x == 0, np.nan, x)

            avg_l_num = int(np.nanmean(at_zero2nan(cut_long_num))) if np.any(cut_long_num) else 0
            avg_s_num = int(np.nanmean(at_zero2nan(cut_short_num))) if np.any(cut_short_num) else 0
            if if_plot:
                # 5. 绘图 - 美化版样式
                import matplotlib.patches as mpatches

                # 设置全局字体
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False

                fig, ax = plt.subplots(figsize=(12, 7))

                # 更现代的背景样式
                fig.patch.set_facecolor('#f5f5f5')
                fig.patch.set_alpha(0.95)
                ax.set_facecolor('#ffffff')

                # 更精致的网格线
                ax.grid(True, which='major', color='#e0e0e0', linestyle='-', linewidth=0.8, alpha=0.6)
                ax.grid(True, which='minor', color='#f0f0f0', linestyle=':', linewidth=0.5, alpha=0.4)
                ax.minorticks_on()

                # 绘制曲线 - 使用更美观的颜色和样式
                ax.plot(cut_dates, long_pnl, color='#2E86AB', label='Long', linewidth=2.0, alpha=0.85, zorder=3)
                ax.plot(cut_dates, short_pnl, color='#A23B72', label='Short', linewidth=2.0, alpha=0.85, zorder=3)
                ax.plot(cut_dates, net_strategy, color='#F18F01', label=('Strategy' if alpha_id == None else alpha_id),
                        linewidth=2.5, zorder=4, marker='', solid_joinstyle='round')

                # 添加填充效果，增强可读性
                ax.fill_between(cut_dates, 0, net_strategy, alpha=0.08, color='#F18F01', zorder=1)

                # 格式化X轴
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

                # 更美观的标题样式
                header = (f"SR: {sr:.3f}  |  Ret: {ann_ret:.3%}  |  TVR: {tvr_avg:.3f}  |  "
                          f"Num: {avg_l_num}|{avg_s_num}  |  DD: {dd:.1f}%  |  "
                          f"Period: {cut_dates[0].strftime('%Y-%m-%d')} ~ {cut_dates[-1].strftime('%Y-%m-%d')}")

                # 主标题 - 使用更现代的方式
                ax.text(0.02, 0.98, header, transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', fontfamily='monospace',
                        bbox=dict(boxstyle='round', facecolor='#f8f8f8', edgecolor='#cccccc', alpha=0.8))

                # Y轴标签
                ax.set_ylabel('Cumulative P&L (Currency Units ×10⁴)', fontsize=11, fontweight='medium', labelpad=10)
                ax.set_xlabel('Date', fontsize=11, fontweight='medium', labelpad=10)

                # 更精致的图例 - 移到右上角（修改这里）
                legend = ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), fontsize=10, frameon=True,
                                   framealpha=0.95, edgecolor='#d0d0d0', fancybox=True, shadow=True)
                legend.get_frame().set_facecolor('#ffffff')

                # 设置坐标轴颜色和样式
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#888888')
                ax.spines['bottom'].set_color('#888888')
                ax.spines['left'].set_linewidth(1.2)
                ax.spines['bottom'].set_linewidth(1.2)

                # 设置刻度样式
                ax.tick_params(axis='both', which='major', labelsize=9, colors='#555555')
                ax.tick_params(axis='x', rotation=30, length=5, width=0.8)
                ax.tick_params(axis='y', length=4, width=0.8)

                # --- 强制设置起始和结束日期刻度 ---
                # 选取 5-6 个均匀分布的中间点 + 明确的起点和终点
                num_ticks = 7
                if len(cut_dates) > num_ticks:
                    # 选取均匀分布的索引
                    idx = np.linspace(0, len(cut_dates) - 1, num_ticks).astype(int)
                    display_dates = cut_dates[idx]
                else:
                    display_dates = cut_dates

                # 设置刻度位置和标签
                ax.set_xticks(display_dates)
                ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in display_dates],
                                   rotation=30, ha='right', fontsize=9)

                # 确保 X 轴范围严格对齐
                ax.set_xlim(cut_dates[0], cut_dates[-1])

                # 添加零线
                ax.axhline(y=0, color='#999999', linestyle='--', linewidth=0.8, alpha=0.5, zorder=2)

                # 添加轻微的水印效果 - 显示策略名称
                if alpha_id:
                    ax.text(0.98, 0.02, f"Alpha: {alpha_id}", transform=ax.transAxes,
                            fontsize=8, color='#cccccc', ha='right', va='bottom', alpha=0.6)

                # 自动调整Y轴边距，让曲线更舒适
                y_margin = (np.nanmax(net_strategy) - np.nanmin(net_strategy)) * 0.05
                ax.set_ylim(
                    bottom=np.nanmin([np.nanmin(long_pnl), np.nanmin(short_pnl), np.nanmin(net_strategy)]) - y_margin,
                    top=np.nanmax([np.nanmax(long_pnl), np.nanmax(short_pnl), np.nanmax(net_strategy)]) + y_margin)

                plt.tight_layout(pad=1.5)
                if save_path != None:
                    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#f5f5f5')
                plt.show()

            return {
                'ann_ret': ann_ret,
                'ann_vol': ann_vol,
                'sr': sr,
                'dd': dd,
                'tvr_avg': tvr_avg,
            }

        except Exception:
            traceback.print_exc()

    def compute_ic(self, alpha, price='vwap', lag=1):
        """
        计算IC和Rank IC的均值
        :param alpha: np.ndarray (Stock, Date) - 因子矩阵
        :param price: 价格字段
        :param lag: 预测天数
        :return: dict {'ic': float, 'rank_ic': float}
        """
        import scipy.stats as stats
        
        ret = op.ts_ret(self.context[price], lag)
        
        alpha_aligned = alpha[:, :-lag]
        ret_aligned = ret[:, lag:]
        
        n_dates = alpha_aligned.shape[1]
        ic_list = []
        rank_ic_list = []
        
        for d in range(n_dates):
            f = alpha_aligned[:, d]
            r = ret_aligned[:, d]
            mask = ~np.isnan(f) & ~np.isnan(r)
            
            if np.sum(mask) > 30:
                ic_val = np.corrcoef(f[mask], r[mask])[0, 1]
                ic_list.append(ic_val)
                
                rank_ic_val, _ = stats.spearmanr(f[mask], r[mask])
                rank_ic_list.append(rank_ic_val)
        
        ic_arr = np.array(ic_list)
        rank_ic_arr = np.array(rank_ic_list)
        
        return {
            'ic': np.nanmean(ic_arr),
            'rank_ic': np.nanmean(rank_ic_arr)
        }

    def compute_ic_decay(self, alpha, price='vwap', max_lag=10):
        """
        计算IC衰减曲线
        :param alpha: np.ndarray (Stock, Date) - 因子矩阵
        :param price: 价格字段
        :param max_lag: 最大滞后天数
        :return: dict {lag: {'ic': float, 'rank_ic': float}}
        """
        decay_results = {}
        
        for lag in range(1, max_lag + 1):
            ic_result = self.compute_ic(alpha, price, lag)
            decay_results[lag] = {
                'ic': ic_result['ic'],
                'rank_ic': ic_result['rank_ic']
            }
        
        return decay_results


# # --- 快速运行脚本 ---
# if __name__ == "__main__":
#     enddate = '20251231'
#     # 1. 初始化执行器
#     executor = AlphaExecutor(data_dir=f'/Users/admin/Downloads/OpenAlpha-main/data/{enddate}')
#
#     # 2. 定义测试表达式
#     # 假设 data 下有 close.csv 和 volume.csv
#     test_formulas = [
#         "cs_zscore(ts_mean(close, 20) / ts_delay(close, 1) - 1)",
#         "ts_correlation(close, volume, 10)",
#         "np.where(close > ts_delay(close, 1), 1, -1)"
#     ]
#
#     # 3. 循环计算并保存结果
#     for i, formula in enumerate(test_formulas):
#         alpha_res = executor.evaluate(formula)
#         if alpha_res is not None:
#             print(f"Alpha_{i} 计算完成，均值: {np.nanmean(alpha_res):.4f}")
#             # 这里可以接你之前的 backtest 函数



#  在expr跑不会污染alpha_pool，也没有变量共享的问题；
#  在expr跑更加纯粹

# --- 快速运行脚本 ---
# 已经筛选中证500~
if __name__ == "__main__":
    enddate = '20251231'

    # 1. 初始化并一次性加载所有基础数据
    executor = AlphaExecutor(data_dir=f'/Users/admin/Downloads/OpenAlpha-main/data/{enddate}')
    executor.load_all_data()

    # 2. 编写你想快速验证的【原始因子表达式】
    # 💡 提示：在这里你只需要写最纯粹的逻辑，不需要手动加任何中证500的外壳了！
    test_formulas = [
        "ts_mean(cs_rank(vwap-close),3)",
        "ts_mean(vwap-close,5)",
        "cs_rank(cs_rank(open)-cs_rank(ts_delay(close,1)))",
        "ts_correlation(ts_ret(low,1),ret1,3)"
    ]

    # 3. 自动化流水线：全自动套壳、计算、回测、切片并画图
    for i, raw_expr in enumerate(test_formulas):
        #【核心改动】：动态合成严格的中证500筛选和洗白逻辑字符串
        final_formula = f'at_nan2zero(cs_booksize(cs_rank(at_mask({raw_expr},ts_fill(csi_500_weight)>0))-0.5))'

        # 3.1 计算套壳后的标准因子得分矩阵
        # alpha_res返回的是一个已经计算好因子值——经过中证500筛选——经过多空分离——经过截面排序cs_rank——经过权重归一化(将多空权重转为交易权重)——Nan转0清洗的矩阵
        alpha_res = executor.evaluate(final_formula)

        if alpha_res is not None:
            # 3.2 运行组合回测
            # bt_result返回的是回测的结果;
            bt_result = executor.backtest(alpha_res)

            # 3.3 切片查看这10年的核心指标并弹窗画图
            executor.simres_cut(
                res=bt_result,
                start_date='20150101',
                end_date='20251231',
                if_plot=True,
                alpha_id=f"Alpha_{i}"
            )
