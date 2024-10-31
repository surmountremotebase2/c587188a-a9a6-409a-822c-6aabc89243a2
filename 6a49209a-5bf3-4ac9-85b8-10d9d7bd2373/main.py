from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InsiderTrading, FinancialStatement
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]
        # Include both InsiderTrading and FinancialStatement in data_list
        self.data_list = [InsiderTrading("AAPL"), FinancialStatement("AAPL")]

    @property
    def interval(self):
        # Daily analysis for simplicity, though real strategies might need finer resolutions
        return "1day"
    
    @property
    def assets(self):
        return self.tickers
    
    @property
    def data(self):
        return self.data_list
    
    def run(self, data):
        allocation_dict = {"AAPL": 0.5}  # Start with a baseline allocation
        
        # Process insider trading data
        insider_data = data.get(("insider_trading", "AAPL"), [])
        if insider_data:
            recent_insider_activity = insider_data[-1]
            if recent_insider_activity['transactionType'].startswith("P"):  # Purchase
                allocation_dict["AAPL"] += 0.25
            elif 'S' in recent_insider_activity['transactionType']:  # Sale
                allocation_dict["AAPL"] -= 0.25
        
        # Process financial statement data for net income analysis
        financial_data = data.get(("financial_statement", "AAPL"), [])
        if len(financial_data) >= 2:
            most_recent = financial_data[-1]
            previous = financial_data[-2]
            
            if most_recent['netIncome'] > previous['netIncome']:
                allocation_dict["AAPL"] += 0.25  # Increase for positive net income growth
            else:
                allocation_dict["AAPL"] -= 0.25  # Decrease for negative growth
        
        # Ensure allocation remains within bounds [0, 1]
        allocation_dict["AAPL"] = max(0, min(1, allocation_dict["AAPL"]))
        
        return TargetAllocation(allocation_dict)