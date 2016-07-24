# encoding: UTF-8

"""
海龟交易策略测试版
"""

from .ctaBase import *
from .ctaTemplate import CtaTemplate
import numpy as np
import talib as ta


########################################################################
class TurtleDemo(CtaTemplate):
    """海龟策略Demo"""
    className = 'TurtleDemo'
    author = 'LL'

    # 策略参数
    breakLength = 20  # 20日突破入市
    exitLength = 10  # 10日离市退出
    atrLength = 21  # atr波动周期为20日
    riskRatio = 2  # 账户波动风险，海龟默认为账户值的2%
    MaxOverWeight = 4  # 最大加仓次数

    initDays = 100  # 初始化数据所用的天数
    holdDays = 30  # 用于计算保留的最大K线数量
    # 策略变量
    bar = None
    barMinute = EMPTY_STRING
    barDate = EMPTY_STRING

    barcounter = EMPTY_INT  # K线计数器，K线数大于初始化天数之后，才正式启用策略计算

    OpenHistory = []  # 开盘价历史数据
    CloseHistory = []  # 收盘价历史数据
    HighHistory = []  # 最高价历史数据
    LowHistory = []  # 最低价历史数据
    VolHistory = []  # 交易量历史数据

    # K线组合历史数据
    HistoryBar = {
        'open': np.array(OpenHistory),
        'high': np.array(HighHistory),
        'low': np.array(LowHistory),
        'close': np.array(CloseHistory),
        'volume': np.array(VolHistory)
    }

    MyPosition = EMPTY_INT  # 持仓方向，空仓0,多头1,空头-1
    PreEnterPrice = EMPTY_FLOAT  # 上一次开仓价格
    OverCounter = EMPTY_INT  # 已加仓次数
    CurBarTrade = EMPTY_INT  # 当日进行过交易标志:无交易:0,开头:1,平多:2,开空:-1,平空:-2
    TotalEquity = EMPTY_INT  # 当前总资金
    TurtleUnits = EMPTY_INT  # 每次开仓手数

    EnterLong = np.array([])  # 多头突破开仓价格
    EnterShort = np.array([])  # 空头突破开仓价格

    ExitLong = np.array([])  # 多头平仓价格
    ExitShort = np.array([])  # 空头平仓价格

    MyATR = np.array([])  # ATR
    N = EMPTY_FLOAT  # 海龟N值

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'breakLength',
                 'exitLength',
                 'atrLength',
                 'riskRatio']

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'PreEnterPrice',
               'OverCounter',
               'CurBarTrade',
               'N']

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(TurtleDemo, self).__init__(ctaEngine, setting)

    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略初始化')

        initData = self.loadDayBar(self.initDays)
        for bar in initData:
            self.onDayBar(bar)
        self.inited = True

        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略启动')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略停止')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        # 计算K线
        tickMinute = tick.datetime.minute

        if tickMinute != self.barMinute:
            if self.bar:
                self.onBar(self.bar)

            bar = CtaBarData()
            bar.vtSymbol = tick.vtSymbol
            bar.symbol = tick.symbol
            bar.exchange = tick.exchange

            bar.open = tick.lastPrice
            bar.high = tick.lastPrice
            bar.low = tick.lastPrice
            bar.close = tick.lastPrice

            bar.date = tick.date
            bar.time = tick.time
            bar.datetime = tick.datetime  # K线的时间设为第一个Tick的时间

            # 实盘中用不到的数据可以选择不算，从而加快速度
            # bar.volume = tick.volume
            # bar.openInterest = tick.openInterest

            self.bar = bar  # 这种写法为了减少一层访问，加快速度
            self.barMinute = tickMinute  # 更新当前的分钟

        else:  # 否则继续累加新的K线
            bar = self.bar  # 写法同样为了加快速度

            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)
            bar.close = tick.lastPrice

        if self.bar and self.inited:
            self.doStrategy(bar)

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""

        pass

    """
        if barcounter>initDays:

            if not MyPosition:        
                if bar.high>EnterLong[-2]:

                
            else:
                self.fastMa1 = self.fastMa0
                self.fastMa0 = bar.close * self.fastK + self.fastMa0 * (1 - self.fastK)
                self.fastMa.append(self.fastMa0)
                
                
            # 判断买卖
            crossOver = self.fastMa0>self.slowMa0 and self.fastMa1<self.slowMa1     # 金叉上穿
            crossBelow = self.fastMa0<self.slowMa0 and self.fastMa1>self.slowMa1    # 死叉下穿
            
            # 金叉和死叉的条件是互斥
            # 所有的委托均以K线收盘价委托（这里有一个实盘中无法成交的风险，考虑添加对模拟市价单类型的支持）
            if crossOver:
                # 如果金叉时手头没有持仓，则直接做多
                if self.pos == 0:
                    self.buy(bar.close, 1)
                # 如果有空头持仓，则先平空，再做多
                elif self.pos < 0:
                    self.cover(bar.close, 1)
                    self.buy(bar.close, 1)
            # 死叉和金叉相反
            elif crossBelow:
                if self.pos == 0:
                    self.short(bar.close, 1)
                elif self.pos > 0:
                    self.sell(bar.close, 1)
                    self.short(bar.close, 1)
                    
        # 发出状态更新事件
        self.putEvent()"""

    # ----------------------------------------------------------------------
    def onDayBar(self, bar):
        """收到日线Bar推送（必须由用户继承实现）"""
        """if not self.barcounter:
            output=open('record.log','w')
            output.close()"""
        # 只有在收到日线BAR时计算所有指标值
        self.updateDAC(bar)

        # 只有K线数达到初始数量以上之后，才开始策略计算
        if self.barcounter > self.breakLength:
            self.doStrategy(bar)
            # 为了历史数据策略测试时,一日内平仓并开反向仓位情况,再执行一遍策略
            # self.doStrategy(self,bar)

        """output=open('record.log','a')
        output.write(u'date %s, 20high %s,20low %s,10high %s 10low %s,Today high %s, low %s, position %s , N %s' 
                    %(bar.date,self.EnterLong[-2],self.EnterShort[-2],self.ExitShort[-2],self.ExitLong[-2],
                      bar.high,bar.low,self.MyPosition,self.N)+'\n')
        output.close()"""

        # 发出状态更新事件
        self.putEvent()

    # ----------------------------------------------------------------------
    def updateDAC(self, bar):
        """收到最新日Ｋ线更新策略所需指标"""
        if bar.date != self.barDate:
            self.barDate = bar.date
            # K线计数
            self.barcounter = self.barcounter + 1
            # 重置当日交易状态
            self.CurBarTrade = 0

            if self.barcounter > self.holdDays:
                self.OpenHistory.pop(0)
                self.CloseHistory.pop(0)
                self.HighHistory.pop(0)
                self.LowHistory.pop(0)
                self.VolHistory.pop(0)

            # 更新K线历史数据
            self.OpenHistory.append(bar.open)
            self.CloseHistory.append(bar.close)
            self.HighHistory.append(bar.high)
            self.LowHistory.append(bar.low)
            self.VolHistory.append(bar.volume)
            self.HistoryBar = {
                'open': np.array(self.OpenHistory, dtype=np.float64),
                'high': np.array(self.HighHistory, dtype=np.float64),
                'low': np.array(self.LowHistory, dtype=np.float64),
                'close': np.array(self.CloseHistory, dtype=np.float64),
                'volume': np.array(self.VolHistory)
            }
            # if self.barcounter>self.breakLength:
            # 更新ATR
            self.MyATR = ta.ATR(self.HistoryBar['high'], self.HistoryBar['low'],
                                self.HistoryBar['close'], timeperiod=self.atrLength)
            if self.MyATR.size > 5:
                # 更新N值
                self.N = round(self.MyATR[-2])
            # 更新入场开仓价格
            self.EnterLong = ta.MAX(self.HistoryBar['high'], timeperiod=self.breakLength)
            self.EnterShort = ta.MIN(self.HistoryBar['low'], timeperiod=self.breakLength)
            # 更新离场平仓价格
            self.ExitLong = ta.MIN(self.HistoryBar['low'], timeperiod=self.exitLength)
            self.ExitShort = ta.MAX(self.HistoryBar['high'], timeperiod=self.exitLength)

    # ----------------------------------------------------------------------
    def doStrategy(self, bar):
        # 已持有多头仓位时
        if self.MyPosition > 0:
            # 当最新K线高点高于上一买入价格以上0.5倍N值，并且加仓次数小于最大允许开仓次数时
            while bar.high >= (self.PreEnterPrice + 0.5 * self.N) and self.OverCounter < self.MaxOverWeight:
                pass
                # 如开盘价格跳空高于上一买入价格以上0.5倍N值价格，则以开盘价格买入
                self.buy(max(bar.open, self.PreEnterPrice + 0.5 * self.N), 1)
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, PreEnterPrice %s, buy price %s'
                             % (bar.date, self.PreEnterPrice, max(bar.open, self.PreEnterPrice + 0.5 * self.N)) + '\n')
                output.close()
                # 更新开仓次数计数器
                self.OverCounter = self.OverCounter + 1
                # 更新记录开仓价格
                self.PreEnterPrice = max(bar.open, self.PreEnterPrice + 0.5 * self.N)
                # 重置当日交易状态
                self.CurBarTrade = 1
            # 如果最新K线低点，低于止损价格（止损价格为2N止损和10日低点中价格更高的那个）
            if bar.low <= max(self.ExitLong[-2], self.PreEnterPrice - 2 * self.N) \
                    and not self.CurBarTrade:
                # 卖平所有持仓
                self.sell(min(bar.open, max(self.ExitLong[-2], self.PreEnterPrice - 1 * self.N)), 1 * self.OverCounter)
                # 初始化持仓状态和开仓次数
                self.OverCounter = 0
                self.MyPosition = 0
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, PreEnterPrice %s, sell price %s'
                             % (bar.date, self.PreEnterPrice,
                                min(bar.open, max(self.ExitLong[-2], self.PreEnterPrice - 2 * self.N))) + '\n')
                output.close()
                # 重置当日交易状态
                self.CurBarTrade = 2
        # 已有空头仓位时
        if self.MyPosition < 0:
            # 当最新K线高点低于上一卖出价格以下0.5倍N值，并且加仓次数小于最大允许开仓次数时
            while bar.low <= (self.PreEnterPrice - 0.5 * self.N) and self.OverCounter < self.MaxOverWeight:
                pass
                # 如开盘价格跳空低于上一卖出价格以下0.5倍N值价格，则以开盘价格卖出
                self.short(min(bar.open, self.PreEnterPrice - 0.5 * self.N), 1)
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, PreEnterPrice %s, short price %s'
                             % (bar.date, self.PreEnterPrice, min(bar.open, self.PreEnterPrice - 0.5 * self.N)) + '\n')
                output.close()
                # 更新开仓次数计数器
                self.OverCounter = self.OverCounter + 1
                # 更新记录开仓价格
                self.PreEnterPrice = min(bar.open, self.PreEnterPrice - 0.5 * self.N)
                # 重置当日交易状态
                self.CurBarTrade = -1
            # 如果最新K线高点，高于止损价格（止损价格为2N止损和10日高点中价格更低的那个）
            if bar.high >= min(self.ExitShort[-2], self.PreEnterPrice + 2 * self.N) \
                    and not self.CurBarTrade:
                # 买平所有持仓
                self.cover(max(bar.open, min(self.ExitShort[-2], self.PreEnterPrice + 2 * self.N)),
                           1 * self.OverCounter)
                # 初始化持仓状态和开仓次数
                self.OverCounter = 0
                self.MyPosition = 0
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, PreEnterPrice %s, cover price %s'
                             % (bar.date, self.PreEnterPrice,
                                max(bar.open, min(self.ExitShort[-2], self.PreEnterPrice + 2 * self.N))) + '\n')
                output.close()
                # 重置当日交易状态
                self.CurBarTrade = -2
        # 空仓时，突破入市价格新高、新低时开仓
        if self.MyPosition == 0:
            # 最新K线高点超过上一日多头突破价格时开仓
            if bar.high >= self.EnterLong[-2] and self.CurBarTrade != 2:
                # 如开盘价格跳空高于多头突破价格，则以开盘价格买入
                self.buy(max(bar.open, self.EnterLong[-2]), 1)
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, PreEnterPrice %s, buy price %s'
                             % (bar.date, self.PreEnterPrice, (max(bar.open, self.EnterLong[-2]), 1)) + '\n')
                output.close()
                # 更新开仓次数计数器
                self.OverCounter = self.OverCounter + 1
                # 记录开仓价格
                self.PreEnterPrice = max(bar.open, self.EnterLong[-2])
                # 设置为持有多头仓位
                self.MyPosition = 1
                # 重置当日交易状态
                self.CurBarTrade = 1
            # 最新K线低点低于上一日空头突破价格
            if bar.low <= self.EnterShort[-2] and self.CurBarTrade != -2:
                # 如果开盘价格跳空低开，低于空头突破价格，则以开盘价格卖出
                self.short(min(bar.open, self.EnterShort[-2]), 1)
                # 日志输出
                output = open('record.log', 'a')
                output.write('date %s, short price %s'
                             % (bar.date, min(bar.open, self.EnterShort[-2])) + '\n')
                output.close()
                # 更新开仓次数计数器
                self.OverCounter = self.OverCounter + 1
                # 记录开仓价格
                self.PreEnterPrice = min(bar.open, self.EnterShort[-2])
                # 设置为持有空头仓位
                self.MyPosition = -1
                # 重置当日交易状态
                self.CurBarTrade = -1

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass


########################################################################################
class OrderManagementDemo(CtaTemplate):
    """基于tick级别细粒度撤单追单测试demo"""

    className = 'OrderManagementDemo'
    author = '用Python的交易员'

    # 策略参数
    initDays = 10  # 初始化数据所用的天数

    # 策略变量
    bar = None
    barMinute = EMPTY_STRING

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol']

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos']

    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(OrderManagementDemo, self).__init__(ctaEngine, setting)

        self.lastOrder = None
        self.orderType = ''

    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略初始化')

        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)

        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略启动')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog('海龟演示策略停止')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""

        # 建立不成交买单测试单        
        if self.lastOrder == None:
            self.buy(tick.lastprice - 10.0, 1)

        # CTA委托类型映射
        if self.lastOrder != None and self.lastOrder.direction == '多' and self.lastOrder.offset == '开仓':
            self.orderType = '买开'

        elif self.lastOrder != None and self.lastOrder.direction == '多' and self.lastOrder.offset == '平仓':
            self.orderType = '买平'

        elif self.lastOrder != None and self.lastOrder.direction == '空' and self.lastOrder.offset == '开仓':
            self.orderType = '卖开'

        elif self.lastOrder != None and self.lastOrder.direction == '空' and self.lastOrder.offset == '平仓':
            self.orderType = '卖平'

        # 不成交，即撤单，并追单
        if self.lastOrder != None and self.lastOrder.status == '未成交':

            self.cancelOrder(self.lastOrder.vtOrderID)
            self.lastOrder = None
        elif self.lastOrder != None and self.lastOrder.status == '已撤销':
            # 追单并设置为不能成交

            self.sendOrder(self.orderType, self.tick.lastprice - 10, 1)
            self.lastOrder = None

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        self.lastOrder = order

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
