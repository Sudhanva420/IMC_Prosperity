from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import numpy as np

class Trader:
    def __init__(self):
        self.price_history = {}  # Store price history for each product

    def run(self, state: TradingState):
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: List[Order] = []
            best_bid = max(order_depth.buy_orders.keys(), default=None)
            best_ask = min(order_depth.sell_orders.keys(), default=None)

            if best_bid is None or best_ask is None:
                continue  # Skip if no valid data

            mid_price = (best_bid + best_ask) / 2  # Midpoint price
            self.update_price_history(product, mid_price)

            if len(self.price_history[product]) < 3:
                continue  # Skip if not enough data

            # Compute 3-period SMA (short-term trend)
            sma = np.mean(self.price_history[product][-3:])

            # Simple trend-following strategy
            if mid_price > sma:  # Uptrend detected
                orders.append(Order(product, best_ask, 10))  # Buy at best ask
            elif mid_price < sma:  # Downtrend detected
                orders.append(Order(product, best_bid, -10))  # Sell at best bid

            result[product] = orders

        return result, 0, "Momentum Strategy"

    def update_price_history(self, product: str, price: float):
        """ Maintain a short history of prices for trend detection """
        if product not in self.price_history:
            self.price_history[product] = []
        
        self.price_history[product].append(price)
        
        # Keep only the last 5 prices to limit memory usage
        if len(self.price_history[product]) > 5:
            self.price_history[product].pop(0)
