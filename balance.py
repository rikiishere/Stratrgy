import time


class mid_class():
    def __init__(self, this_exchange):
        #         初始化数据
        #         填充交易所的信息  首次获取价格  首次获取account信息
        #         设定密钥
        '''
        args:
        init_timestamp:获取时间
        exchange:交易所
        name:名称
        currency:交易对
        '''
        self.init_timestamp = time.time()
        self.exchange = this_exchange
        self.Name = self.exchange.GetName()
        self.Currency = self.exchange.GetCurrency()

    def get_account(self):
        #         获取账户信息
        '''
        args:
        account:账户信息
        Balance:金额
        FrozenBalance:冻结金额
        Stocks:币数
        FrozenStocks:剩余币数
        '''
        self.Balance = '--'
        self.FrozenBalance = '--'
        self.Stocks = '--'
        self.FrozenStocks = '--'

        try:
            self.account = self.exchange.GetAccount()
            self.Balance = self.account['Balance']
            self.FrozenBalance = self.account['FrozenBalance']
            self.Stocks = self.account['Stocks']
            self.FrozenStocks = self.account['FrozenStocks']
            return True
        except:
            return False

    def get_ticker(self):
        #         获取市价信息
        '''
        args:
         价格信息
        '''
        self.High = '--'
        self.Low = '--'
        self.Sell = '--'
        self.Buy = '--'
        self.Last = '--'
        self.Volume = '--'
        try:
            self.ticker = self.exchange.GetTicker()
            self.High = self.ticker['High']
            self.Low = self.ticker['Low']
            self.Sell = self.ticker['Sell']
            self.Buy = self.ticker['Buy']
            self.Last = self.ticker['Last']
            self.Volume = self.ticker['Volume']
            return True
        except:
            return False

    def get_depth(self):
        #         获取深度信息
        self.Asks = '--'
        self.Bids = '--'
        try:
            self.depth = self.exchange.GetDepth()
            self.Asks = self.depth['Asks']
            self.Bids = self.depth['Bids']
            return True
        except:
            return False

    def get_ohlc_data(self, period=PERIOD_M5):
        #         获取k线信息
        #         返回一个K线历史,K线周期在创建机器人时指定，如果在调用exchange.GetRecords()函数时指定了参数，
        #         获取的就是按照该参数周期的K线数据，如果没有参数，按照机器人参数上设置的K线周期或者回测页面设置的K线周期返回K线数据。
        #         参数值:PERIOD_M1指1分钟,PERIOD_M5指5分钟,PERIOD_M15指15分钟,PERIOD_M30指30分钟,PERIOD_H1指1小时,PERIOD_D1指一天。
        #         返回值:Record结构体数组。K线数据，会随时间累积，最多累积到2000根，然后会更新加入一根，同时删除一根最早时间的K线柱（如队列进出）。
        #         部分交易所没有提供K线接口，托管者实时收集数据生成K线。
        self.ohlc_data = self.exchange.GetRecords(period)

    def create_order(self, order_type, price, amount):
        #         post一个挂单信息
        '''下买单,返回一个订单ID。参数值：price为订单价格，number类型，Amount为订单数量，number类型。
        返回值：string类型或数值类型（具体类型根据各个交易所返回类型而定）。'''
        if order_type == 'Buy':
            try:
                order_id = self.exchange.Buy(price, amount)
                return order_id
            except:
                return False
        elif order_type == 'Sell':
            try:
                order_id = self.exchange.Sell(price, amount)
                return order_id
            except:
                return False
        

    def cancel_order(self, order_id):
        #         取消一个挂单信息
        return self.exchange.CancelOrder(order_id)

    def refresh_data(self):
        #         刷新信息
        if not self.get_account():
            return 'get_account error'
        if not self.get_ticker():
            return 'get_ticker error'
        if not self.get_depth():
            return 'get_depth error'
        try:
            self.get_ohlc_data()
        except:
            return 'get_ohlc_data error'
        return 'refresh_data finish'
    
class Balance_Strategy():
    def __init__(self,mid_class):
        self.exchange=mid_class
        self.last_trade_price=self.exchange.Last
        self.buy_count=0
        self.sell_count=0
    
    def account_info(self):
        self.exchange.refresh_data()
        self.coin=self.exchange.Stocks
        self.balance=self.exchange.Balance
        now_price=self.last_trade_price
                
        self.total_balance=self.coin*now_price+self.balance
        self.half=self.total_balance/2
        self.need_buy=(self.half-self.coin*now_price)/now_price
        self.need_sell=(self.half-self.balance)/now_price
    
    def do_balance(self):
        if self.need_buy > 0:
            self.exchange.create_order('Buy',self.exchange.Low,self.need_buy)
            self.buy_count +=1
        elif self.need_sell > 0:
            self.exchange.create_order('Sell',self.exchange.High,self.need_sell)
            self.sell_count+=1

    def if_need_trade(self,param):
        Log((self.last_trade_price))
        Log((self.exchange.Last))
        if abs(self.exchange.Last-self.last_trade_price)/self.last_trade_price > param:
            self.do_balance()
            self.last_trade_price=self.exchange.Last
            
        
        
            
        
def main():
    mid=mid_class(exchange)
    Log(mid.refresh_data())
    bs=Balance_Strategy(mid)
    
    while (True):
        Sleep(60*5)
        bs.account_info()
        bs.if_need_trade(0.04)
    Log('buy_count',bs.buy_count)
    Log('sell_count',bs.sell_count)