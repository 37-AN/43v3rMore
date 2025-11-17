"""
Quantum Trading Analysis Engine
Based on MQL5 Article 17171: Quantum Computing for Market Analysis

This module implements:
1. Quantum Phase Estimation (QPE) for market cycle detection
2. Price superposition analysis for simultaneous path evaluation
3. Pattern prototype discovery using quantum algorithms
4. Integration with MetaTrader 5 for real-time data
"""

import numpy as np
import pandas as pd
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from typing import List, Dict, Tuple, Optional
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuantumTradingEngine:
    """
    Main quantum trading analysis engine combining quantum computing
    with classical technical analysis for enhanced market prediction.
    """
    
    def __init__(self, 
                 symbols: List[str] = ['EURUSD', 'GBPUSD', 'USDZAR'],
                 timeframe: str = 'H1',
                 lookback_periods: int = 100):
        """
        Initialize the quantum trading engine.
        
        Args:
            symbols: List of trading symbols to analyze
            timeframe: MT5 timeframe (H1, M15, D1, etc.)
            lookback_periods: Number of historical bars to analyze
        """
        self.symbols = symbols
        self.timeframe = self._parse_timeframe(timeframe)
        self.lookback_periods = lookback_periods
        self.simulator = Aer.get_backend('qasm_simulator')
        
        # Initialize MT5 connection
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            raise ConnectionError("Failed to connect to MetaTrader 5")
        
        logger.info(f"Quantum Trading Engine initialized for {symbols}")
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Convert timeframe string to MT5 constant."""
        timeframes = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
        }
        return timeframes.get(timeframe, mt5.TIMEFRAME_H1)
    
    def get_market_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch historical market data from MT5.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            DataFrame with OHLCV data
        """
        rates = mt5.copy_rates_from_pos(
            symbol, 
            self.timeframe, 
            0, 
            self.lookback_periods
        )
        
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to get data for {symbol}")
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        logger.info(f"Fetched {len(df)} bars for {symbol}")
        return df
    
    def encode_price_to_quantum(self, prices: np.ndarray) -> QuantumCircuit:
        """
        Encode price data into quantum states using amplitude encoding.
        This creates a superposition of all price states simultaneously.
        
        Args:
            prices: Normalized price array
            
        Returns:
            Quantum circuit with encoded price data
        """
        # Normalize prices to range [0, 1]
        normalized_prices = (prices - prices.min()) / (prices.max() - prices.min())
        
        # Determine number of qubits needed
        n_qubits = int(np.ceil(np.log2(len(normalized_prices))))
        
        # Pad prices to power of 2
        padded_prices = np.pad(
            normalized_prices, 
            (0, 2**n_qubits - len(normalized_prices)), 
            mode='constant'
        )
        
        # Normalize to create valid quantum state
        state_vector = padded_prices / np.linalg.norm(padded_prices)
        
        # Create quantum circuit
        qc = QuantumCircuit(n_qubits, name='PriceEncoding')
        qc.initialize(state_vector, range(n_qubits))
        
        return qc
    
    def quantum_phase_estimation(self, 
                                  prices: np.ndarray, 
                                  n_counting_qubits: int = 5) -> Dict[str, float]:
        """
        Perform Quantum Phase Estimation (QPE) to detect market cycles.
        
        This is the core innovation from MQL5 Article 17171:
        - Detects dominant market cycles
        - Estimates period of repeating patterns
        - Provides phase information for timing
        
        Args:
            prices: Price series data
            n_counting_qubits: Number of qubits for phase precision
            
        Returns:
            Dictionary with cycle information and confidence scores
        """
        # Encode prices
        price_circuit = self.encode_price_to_quantum(prices)
        n_system_qubits = price_circuit.num_qubits
        
        # Create QPE circuit
        qr_counting = QuantumRegister(n_counting_qubits, 'counting')
        qr_system = QuantumRegister(n_system_qubits, 'system')
        cr = ClassicalRegister(n_counting_qubits, 'measurement')
        
        qc = QuantumCircuit(qr_counting, qr_system, cr)
        
        # Initialize system register with price data
        qc.compose(price_circuit, qr_system, inplace=True)
        
        # Apply Hadamard to counting qubits
        qc.h(qr_counting)
        
        # Controlled unitary operations (simplified market evolution)
        for i in range(n_counting_qubits):
            repetitions = 2 ** i
            for _ in range(repetitions):
                # Market evolution operator (price momentum)
                qc.cx(qr_counting[i], qr_system[0])
                qc.rz(np.pi / 4, qr_system[0])
        
        # Inverse QFT on counting register
        qc.compose(QFT(n_counting_qubits, inverse=True), qr_counting, inplace=True)
        
        # Measure
        qc.measure(qr_counting, cr)
        
        # Execute
        job = self.simulator.run(qc, shots=10000)
        result = job.result()
        counts = result.get_counts()
        
        # Analyze results
        cycle_info = self._analyze_qpe_results(counts, n_counting_qubits)
        
        logger.info(f"QPE detected cycle: {cycle_info['dominant_cycle']} periods")
        return cycle_info
    
    def _analyze_qpe_results(self, 
                             counts: Dict[str, int], 
                             n_qubits: int) -> Dict[str, float]:
        """
        Analyze QPE measurement results to extract cycle information.
        
        Args:
            counts: Measurement outcomes from QPE
            n_qubits: Number of counting qubits used
            
        Returns:
            Cycle analysis results
        """
        # Convert binary outcomes to phases
        phases = {}
        total_shots = sum(counts.values())
        
        for outcome, count in counts.items():
            # Binary to phase
            phase_value = int(outcome, 2) / (2 ** n_qubits)
            confidence = count / total_shots
            phases[phase_value] = confidence
        
        # Find dominant cycle
        dominant_phase = max(phases.keys(), key=phases.get)
        
        # Convert phase to cycle period
        if dominant_phase > 0:
            cycle_period = 1 / dominant_phase
        else:
            cycle_period = float('inf')
        
        return {
            'dominant_cycle': cycle_period,
            'dominant_phase': dominant_phase,
            'confidence': phases[dominant_phase],
            'all_cycles': phases,
            'cycle_strength': self._calculate_cycle_strength(phases)
        }
    
    def _calculate_cycle_strength(self, phases: Dict[float, float]) -> float:
        """
        Calculate the strength/clarity of detected cycles.
        Higher values indicate stronger, clearer cycles.
        """
        if not phases:
            return 0.0
        
        # Use entropy-based measure
        probabilities = np.array(list(phases.values()))
        if len(probabilities) == 0:
            return 0.0
        
        # Normalized entropy (0 = single strong cycle, 1 = random)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        max_entropy = np.log2(len(probabilities))
        
        if max_entropy == 0:
            return 1.0
        
        # Invert so higher = stronger cycle
        strength = 1 - (entropy / max_entropy)
        return strength
    
    def analyze_superposition(self, prices: np.ndarray) -> Dict[str, any]:
        """
        Analyze all possible price paths in superposition.
        
        This leverages quantum parallelism to evaluate multiple
        scenarios simultaneously, as described in Article 17171.
        
        Args:
            prices: Recent price history
            
        Returns:
            Dictionary with probability distribution of outcomes
        """
        # Create superposition of possible future states
        n_qubits = 4  # 2^4 = 16 possible outcomes
        qc = QuantumCircuit(n_qubits, n_qubits)
        
        # Create superposition
        qc.h(range(n_qubits))
        
        # Apply price momentum encoding
        price_momentum = np.diff(prices[-10:])
        avg_momentum = np.mean(price_momentum)
        
        # Rotate based on momentum (bullish vs bearish bias)
        if avg_momentum > 0:
            # Bullish bias
            for i in range(n_qubits):
                qc.ry(avg_momentum * np.pi / 4, i)
        else:
            # Bearish bias
            for i in range(n_qubits):
                qc.ry(avg_momentum * np.pi / 4, i)
        
        # Measure
        qc.measure(range(n_qubits), range(n_qubits))
        
        # Execute
        job = self.simulator.run(qc, shots=10000)
        result = job.result()
        counts = result.get_counts()
        
        # Analyze outcome distribution
        outcomes = self._analyze_superposition_outcomes(counts)
        
        return outcomes
    
    def _analyze_superposition_outcomes(self, 
                                       counts: Dict[str, int]) -> Dict[str, any]:
        """
        Analyze superposition measurement outcomes to predict direction.
        
        Args:
            counts: Measurement results
            
        Returns:
            Prediction dictionary with probabilities
        """
        total_shots = sum(counts.values())
        
        # Classify outcomes as bullish/bearish/neutral
        bullish_count = 0
        bearish_count = 0
        
        for outcome, count in counts.items():
            # Convert binary to decimal
            value = int(outcome, 2)
            
            # Classify: higher values = bullish, lower = bearish
            if value > 8:  # Above midpoint
                bullish_count += count
            elif value < 8:
                bearish_count += count
        
        bullish_prob = bullish_count / total_shots
        bearish_prob = bearish_count / total_shots
        neutral_prob = 1 - bullish_prob - bearish_prob
        
        # Determine signal
        if bullish_prob > 0.6:
            signal = 'STRONG_BUY'
        elif bullish_prob > 0.55:
            signal = 'BUY'
        elif bearish_prob > 0.6:
            signal = 'STRONG_SELL'
        elif bearish_prob > 0.55:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        return {
            'signal': signal,
            'bullish_probability': bullish_prob,
            'bearish_probability': bearish_prob,
            'neutral_probability': neutral_prob,
            'confidence': max(bullish_prob, bearish_prob),
            'raw_counts': counts
        }
    
    def generate_trading_signal(self, symbol: str) -> Dict[str, any]:
        """
        Generate comprehensive trading signal combining all quantum analyses.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Complete trading signal with entry, stop loss, take profit
        """
        # Get market data
        df = self.get_market_data(symbol)
        if df.empty:
            return {'error': 'No market data available'}
        
        prices = df['close'].values
        
        # Perform quantum analyses
        logger.info(f"Analyzing {symbol} with quantum algorithms...")
        
        # 1. Quantum Phase Estimation for cycles
        cycle_info = self.quantum_phase_estimation(prices)
        
        # 2. Superposition analysis for direction
        superposition_result = self.analyze_superposition(prices)
        
        # 3. Classical confirmation
        current_price = prices[-1]
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        # Combine quantum and classical signals
        signal = self._combine_signals(
            superposition_result,
            cycle_info,
            current_price,
            sma_20,
            sma_50
        )
        
        logger.info(f"Signal generated for {symbol}: {signal['action']}")
        return signal
    
    def _combine_signals(self,
                        quantum_signal: Dict,
                        cycle_info: Dict,
                        current_price: float,
                        sma_20: float,
                        sma_50: float) -> Dict[str, any]:
        """
        Combine quantum and classical signals for final trading decision.
        
        Args:
            quantum_signal: Superposition analysis result
            cycle_info: QPE cycle detection result
            current_price: Current market price
            sma_20: 20-period simple moving average
            sma_50: 50-period simple moving average
            
        Returns:
            Complete trading signal
        """
        # Base signal from quantum analysis
        base_signal = quantum_signal['signal']
        confidence = quantum_signal['confidence']
        
        # Classical confirmation
        trend_bullish = current_price > sma_20 > sma_50
        trend_bearish = current_price < sma_20 < sma_50
        
        # Cycle strength affects confidence
        cycle_strength = cycle_info['cycle_strength']
        adjusted_confidence = confidence * cycle_strength
        
        # Final decision
        if 'BUY' in base_signal and trend_bullish:
            action = 'BUY'
            confidence_multiplier = 1.2
        elif 'SELL' in base_signal and trend_bearish:
            action = 'SELL'
            confidence_multiplier = 1.2
        elif 'BUY' in base_signal:
            action = 'BUY'
            confidence_multiplier = 0.8
        elif 'SELL' in base_signal:
            action = 'SELL'
            confidence_multiplier = 0.8
        else:
            action = 'HOLD'
            confidence_multiplier = 1.0
        
        final_confidence = min(adjusted_confidence * confidence_multiplier, 0.99)
        
        # Calculate entry, SL, TP
        if action == 'BUY':
            entry = current_price
            stop_loss = entry - (entry - sma_20) * 1.5
            take_profit = entry + (entry - stop_loss) * 2
        elif action == 'SELL':
            entry = current_price
            stop_loss = entry + (sma_20 - entry) * 1.5
            take_profit = entry - (stop_loss - entry) * 2
        else:
            entry = current_price
            stop_loss = None
            take_profit = None
        
        return {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'entry_price': round(entry, 5),
            'stop_loss': round(stop_loss, 5) if stop_loss else None,
            'take_profit': round(take_profit, 5) if take_profit else None,
            'confidence': round(final_confidence, 2),
            'quantum_signal': base_signal,
            'cycle_period': round(cycle_info['dominant_cycle'], 1),
            'cycle_strength': round(cycle_strength, 2),
            'trend': 'BULLISH' if trend_bullish else 'BEARISH' if trend_bearish else 'NEUTRAL',
            'risk_reward_ratio': 2.0 if action != 'HOLD' else None
        }
    
    def analyze_all_symbols(self) -> List[Dict[str, any]]:
        """
        Generate signals for all configured symbols.
        
        Returns:
            List of trading signals
        """
        signals = []
        
        for symbol in self.symbols:
            try:
                signal = self.generate_trading_signal(symbol)
                signal['symbol'] = symbol
                signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                signals.append({
                    'symbol': symbol,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return signals
    
    def __del__(self):
        """Cleanup MT5 connection."""
        mt5.shutdown()


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = QuantumTradingEngine(
        symbols=['EURUSD', 'GBPUSD', 'USDZAR', 'XAUUSD'],
        timeframe='H1',
        lookback_periods=100
    )
    
    # Generate signals
    signals = engine.analyze_all_symbols()
    
    # Display results
    print("\n" + "="*60)
    print("QUANTUM TRADING SIGNALS")
    print("="*60 + "\n")
    
    for signal in signals:
        if 'error' not in signal:
            print(f"Symbol: {signal['symbol']}")
            print(f"Action: {signal['action']}")
            print(f"Confidence: {signal['confidence']*100:.1f}%")
            print(f"Entry: {signal['entry_price']}")
            if signal['stop_loss']:
                print(f"Stop Loss: {signal['stop_loss']}")
                print(f"Take Profit: {signal['take_profit']}")
            print(f"Cycle: {signal['cycle_period']} periods")
            print(f"Trend: {signal['trend']}")
            print("-" * 60)
        else:
            print(f"Symbol: {signal['symbol']} - ERROR: {signal['error']}")
            print("-" * 60)
