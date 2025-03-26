from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import numpy as np

class Trader:
    
    def __init__(self):
        self.price_history_kelp = []
        self.price_history_resin = []

    def run(self, state: TradingState):
        result = {}

        for product, order_depth in state.order_depths.items():
            print(f"Processing: {product}")

            if product == "KELP":
                print("Applying KELP strategy")
                orders: List[Order] = []
                best_bid = max(order_depth.buy_orders.keys(), default=None)
                best_ask = min(order_depth.sell_orders.keys(), default=None)

                if best_ask is None or best_bid is None:
                    continue

                mid_price = (best_bid + best_ask) / 2
                self.update_price_history(product, mid_price)

                if len(self.price_history_kelp) < 10:
                    continue

                sma_3 = np.mean(self.price_history_kelp[-3:])
                sma_10 = np.mean(self.price_history_kelp[-10:])
                ROC = ((mid_price - self.price_history_kelp[-5]) / self.price_history_kelp[-5]) * 100

                if sma_3 > sma_10 and ROC > 20:
                    orders.append(Order(product, best_bid, 5))
                    print("BOUGHT KELP")

                elif sma_10 > sma_3 and ROC < 20:
                    orders.append(Order(product, best_ask, -5))
                    print("SOLD KELP")

                result[product] = orders  

            elif product == "RAINFOREST_RESIN":
                print("Applying RAINFOREST_RESIN strategy")
                orders: List[Order] = []
                best_bid = max(order_depth.buy_orders.keys(), default=None)
                best_ask = min(order_depth.sell_orders.keys(), default=None)

                if best_bid is None or best_ask is None:
                    continue  

                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid_volume = order_depth.buy_orders[best_bid]

                mid_price = (best_bid + best_ask) / 2  
                self.update_price_history(product, mid_price)

                if len(self.price_history_resin) < 5:
                    continue 

                sma = np.mean(self.price_history_resin[-5:])

                if mid_price > sma: 
                    orders.append(Order(product, best_ask, best_ask_volume)) 
                    print("SOLD RAINFOREST_RESIN") 

                elif mid_price < sma: 
                    orders.append(Order(product, best_bid, best_bid_volume))
                    print("BOUGHT RAINFOREST_RESIN")

                result[product] = orders  

        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData

    def update_price_history(self, product: str, mid_price: float):
        if product == "KELP":
            price_history = self.price_history_kelp
        else:
            price_history = self.price_history_resin

        price_history.append(mid_price)

        if len(price_history) > 10:
            price_history.pop(0)
