class Guardrail:
    """
    Enforces strict safety rules to prevent the AI from causing financial harm.
    These 'Guardrails' ensure the bot operates within predefined risk limits.
    """
    
    def __init__(self, max_drawdown_pct=0.10, max_position_size_pct=0.05, restricted_assets=None):
        self.max_drawdown_pct = max_drawdown_pct  # Max allowed loss from peak (e.g., 10%)
        self.max_position_size_pct = max_position_size_pct # Max size of a single position relative to portfolio (e.g., 5%)
        self.restricted_assets = restricted_assets or []
        self.peak_value = 0
        
    def check_trade(self, portfolio_value, cash, trade_cost, symbol, current_holdings):
        """
        Validates a trade against safety rules.
        Returns: (bool allowed, str reason)
        """
        # 1. Update peak value tracking
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
            
        # 2. Check for Catastrophic Drawdown
        current_drawdown = (self.peak_value - portfolio_value) / self.peak_value if self.peak_value > 0 else 0
        if current_drawdown > self.max_drawdown_pct:
            return False, f"GUARDRAIL: Max drawdown of {self.max_drawdown_pct*100}% exceeded. Trading halted."
            
        # 3. Check Position Sizing (Don't put all eggs in one basket)
        if trade_cost > (portfolio_value * self.max_position_size_pct):
             return False, f"GUARDRAIL: Trade size {trade_cost:.2f} exceeds {self.max_position_size_pct*100}% of portfolio limit."

        # 4. Check Restricted Assets (Redundancy for EthicalFilter)
        if symbol in self.restricted_assets:
            return False, f"GUARDRAIL: Asset {symbol} is on the restricted list."
            
        return True, "Trade approved by Guardrails."
