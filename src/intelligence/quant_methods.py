import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.neighbors import KernelDensity

class MedallionEngine:
    """
    Implements quantitative methods inspired by James Simons and Renaissance Technologies.
    Focuses on non-parametric statistics, pattern recognition, and regime switching.
    """
    
    def __init__(self):
        self.hmm_model = None
        self.regime_map = {}

    def fit_regime_detection(self, prices):
        """
        Uses Hidden Markov Models (HMM) to classify market states.
        Handles data cleaning for stability.
        """
        # Calculate returns and clean data
        returns = np.diff(np.log(prices))
        returns = returns[~np.isnan(returns) & ~np.isinf(returns)]
        
        if len(returns) < 10: # Minste datagrunnlag
            return "Stable_Growth", np.zeros(len(prices)-1)

        X = returns.reshape(-1, 1)
        
        try:
            # Fit Gaussian HMM with 3 components (Regimes)
            self.hmm_model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
            self.hmm_model.fit(X)
            hidden_states = self.hmm_model.predict(X)
            
            # Heuristic mapping
            variances = [self.hmm_model.covars_[i][0][0] for i in range(3)]
            sorted_indices = np.argsort(variances)
            
            self.regime_map = {
                sorted_indices[0]: "Stable_Growth",
                sorted_indices[1]: "Neutral_Choppy",
                sorted_indices[2]: "High_Risk_Crash"
            }
            
            current_state = hidden_states[-1]
            return self.regime_map[current_state], hidden_states
        except:
            return "Neutral_Choppy", np.zeros(len(returns))

    def predict_next_move_kernel(self, prices, window=5):
        """
        Uses Kernel Density Estimation / Pattern Matching to find similar past windows.
        Simulates Simons' 'Pattern Recognition' approach.
        """
        if len(prices) < window * 2:
            return 0.0

        # Normalize recent window
        recent_window = prices[-window:]
        recent_norm = (recent_window - np.mean(recent_window)) / np.std(recent_window)
        
        # Scan history for similar patterns (Euclidean distance)
        best_match_idx = -1
        min_dist = float('inf')
        
        # Look back
        for i in range(len(prices) - window * 2):
            past_window = prices[i : i+window]
            if np.std(past_window) == 0: continue
            
            past_norm = (past_window - np.mean(past_window)) / np.std(past_window)
            dist = np.linalg.norm(recent_norm - past_norm)
            
            if dist < min_dist:
                min_dist = dist
                best_match_idx = i

        # What happened after the best match?
        if best_match_idx != -1:
            future_price = prices[best_match_idx + window]
            past_price = prices[best_match_idx + window - 1]
            predicted_return = (future_price - past_price) / past_price
            return predicted_return
            
        return 0.0

    def calculate_pairs_zscore(self, asset_a, asset_b, window=30):
        """
        Statistical Arbitrage: Calculates Z-score of the spread between two assets.
        Entry signal if Z-score > 2 or < -2.
        """
        if len(asset_a) != len(asset_b):
            min_len = min(len(asset_a), len(asset_b))
            asset_a = asset_a[-min_len:]
            asset_b = asset_b[-min_len:]
            
        # Log prices
        log_a = np.log(asset_a)
        log_b = np.log(asset_b)
        
        # Calculate spread (mock beta=1 for simplicity)
        spread = log_a - log_b
        
        mean_spread = spread.rolling(window=window).mean()
        std_spread = spread.rolling(window=window).std()
        
        z_score = (spread - mean_spread) / std_spread
        return z_score.iloc[-1]
