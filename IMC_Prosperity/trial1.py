from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
from typing import Tuple

class Trader:
    
    def __init__(self, name:str, min_price_dif:int, max_position:int):
        super().__init__(name,max_position)
        self.strategy_start_day = 2
        
        self.old_bids=[]
        self.bid_asks=[]
        self.new_buy_orders=0
        self.new_sell_orders=0
        self.min_price_dif = min_price_dif
        self.trade_count: int = 1
        
        
    def buy_product(self, best_asks, i, order_depth, orders):
        
        best_ask_volume = order_depth.sell_orders[best_asks[i]]
        
        if self.prod_position >= self.max_pos:
            return  # Dont buy if you aldready have bought max amt

        if self.prod_position + best_ask_volume <= self.max_position:
            orders.append(Order(self.name, best_asks[i],-best_ask_volume)) #We take negative here because sell order quantities--
                                                                           # --are represented with negative sign
            self.prod_position += -best_ask_volume
            self.new_buy_orders += -best_ask_volume
        
        # Vol here is whatever left i can buy without exceeding the max amt
        else:
            vol = self.max_position - self.prod_position
            orders.append(Order(self.name, best_asks[i], vol))
            self.prod_position += -vol
            self.new_buy_orders += vol
    
    def sell_product(self, best_bids, i, order_depth, orders):
        
        if self.prod_position >= self.max_pos:
            return

        best_bid_volume = order_depth.buy_orders[best_bids[i]]
        if self.prod_position + best_bid_volume <= self.max_position:
            orders.append(Order(self.name, best_bids[i], best_bid_volume))
            self.prod_position += -best_bid_volume
            self.new_sell_orders += best_bid_volume
            
        else:
            vol = self.max_position - self.prod_position
            orders.append(Order(self.name, best_bids[i], vol))
            self.prod_position += -vol
            self.new_sell_orders += vol
            
            
    
    def run(self, state: TradingState, orders :list):
        
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
		
        result = {}
        
        #Going through product by product
        for product in state.order_depths:
            order_depth :OrderDepth = state.order_depths[product]
            self.prod_position = state.position.get(product, 0)
            self.cache_prices(order_depth)
            
            if len(self.old_asks) < self.strategy_start_day or len(self.old_bids) < self.strategy_start_day:
                return

            avg_bid, avg_ask = self.calculate_prices(self.strategy_start_day)
            
            
            #In the IF statements, we put i < self.trade_count to just trade once
            if len(order_depth.sell_orders) != 0:
                best_asks = sorted(order_depth.sell_orders.keys())
                
                i=0
                while i < self.trade_count and len(best_asks)>i and best_asks[i] - avg_bid <= self.min_price_dif:
                    if self.prod_position == self.max_position:
                        break
                    
                    self.buy_product(best_asks, i, order_depth, orders)
                    i += 1
                    
            if len(order_depth.buy_orders) != 0:
                best_bids = sorted(order_depth.buy_orders.keys())
                
                i=0
                while i<self.trade_count and len(best_bids)>i and best_bids[i] - avg_ask >= self.min_price_dif:
                    if self.prod_position == self.max_position:
                        break
                    
                    self.sell_product(best_bids, i, order_depth, orders)  
                    i+=1
            
            result[product]=orders
            
            
        traderData = "SAMPLE" 
        
        conversions = 1
        return result, conversions, traderData
    
    
    #Function specifically to calculate avg_prices
    def calculate_prices(self, days:int) -> Tuple[int,int]:
        
        relevant_bids=[]
        for bids in self.old_bids[-days:]:
            relevant_bids.extend([(value,bids[value]) for value in bids])
            
        relevant_asks = []
        for asks in self.old_asks[-days:]:
            relevant_asks.extend([(value, asks[value]) for value in asks])
        
        avg_bid = np.average([x[0] for x in relevant_bids], weights=[x[1]for x in relevant_bids])
        avg_ask = np.average([x[0] for x in relevant_asks], weights=[x[1]for x in relevant_asks])
        
        return avg_bid,avg_ask
        
        
    #This is to like cache old bid and ask orders 
    def cache_prices(self, order_depth: OrderDepth):
        
        buy_orders= order_depth.buy_orders
        sell_orders=order_depth.sell_orders
            
        self.old_bid.append(buy_orders)
        self.old_asks.append(sell_orders)