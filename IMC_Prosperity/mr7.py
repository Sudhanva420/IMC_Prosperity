#WORKS REALLY BAD FOR KELP BUT WORKED WELL FOR RAINFOREST RESIN CAUSE ITS MORE STABLE( IT'LL MOVE AROUND THE MEAN)


from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import numpy as np

class Trader:
    def __init__(self):
        self.price_history = {}

    def run(self, state: TradingState):
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: List[Order] = []
            best_bid = max(order_depth.buy_orders.keys(), default=None)
            best_ask = min(order_depth.sell_orders.keys(), default=None)

            if best_bid is None or best_ask is None:
                continue  

            mid_price = (best_bid + best_ask) / 2  
            self.update_price_history(product, mid_price)

            if len(self.price_history[product]) < 20:
                continue 

            sma = np.mean(self.price_history[product][-20:])

            if mid_price > sma: 
                orders.append(Order(product, best_ask, -5))  
            elif mid_price < sma: 
                orders.append(Order(product, best_bid, 5))

            result[product] = orders

        traderData = "SAMPLE" 

        conversions = 1
        return result, conversions, traderData

    def update_price_history(self, product: str, price: float):
        """ Maintain a short history of prices for trend detection """
        if product not in self.price_history:
            self.price_history[product] = []
        
        self.price_history[product].append(price)

        if len(self.price_history[product]) > 20:
            self.price_history[product].pop(0)
