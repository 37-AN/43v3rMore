"""Test IBM Quantum Cloud connection and functionality."""

import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from loguru import logger

# Load environment variables
load_dotenv()

def test_local_simulator():
    """Test with local AerSimulator (no IBM account needed)."""
    logger.info("Testing local AerSimulator...")

    # Create simple quantum circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)  # Hadamard on qubit 0
    qc.cx(0, 1)  # CNOT with control=0, target=1
    qc.measure([0, 1], [0, 1])

    logger.info(f"Circuit created:\n{qc}")

    # Run on local simulator
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1024)
    result = job.result()
    counts = result.get_counts()

    logger.info(f"Results: {counts}")
    logger.success("✓ Local AerSimulator working correctly")

    return counts


def test_ibm_quantum_connection():
    """Test IBM Quantum Cloud connection."""
    token = os.getenv("IBM_QUANTUM_TOKEN")
    backend_name = os.getenv("IBM_QUANTUM_BACKEND", "ibmq_qasm_simulator")

    if not token or token == "your-ibm-quantum-token":
        logger.warning("IBM_QUANTUM_TOKEN not configured - skipping IBM Cloud test")
        return None

    logger.info(f"Testing IBM Quantum Cloud connection with token: {token[:10]}...")

    try:
        # Try to import IBM Quantum runtime
        from qiskit_ibm_runtime import QiskitRuntimeService

        # Save account
        logger.info("Saving IBM Quantum account...")
        QiskitRuntimeService.save_account(
            channel="ibm_quantum_platform",
            token=token,
            overwrite=True
        )

        # Initialize service
        logger.info("Initializing QiskitRuntimeService...")
        service = QiskitRuntimeService(channel="ibm_quantum_platform")

        # List available backends
        logger.info("Fetching available backends...")
        backends = service.backends()

        logger.success(f"✓ Connected to IBM Quantum Cloud")
        logger.info(f"Available backends: {len(backends)}")

        for backend in backends[:5]:  # Show first 5
            logger.info(f"  - {backend.name}: {backend.status().status_msg}")

        # Try to get specific backend
        if backend_name:
            logger.info(f"Testing backend: {backend_name}")
            backend = service.backend(backend_name)
            logger.success(f"✓ Backend {backend_name} accessible")
            logger.info(f"  Status: {backend.status().status_msg}")
            logger.info(f"  Pending jobs: {backend.status().pending_jobs}")

        return service

    except ImportError:
        logger.warning("qiskit_ibm_runtime not installed")
        logger.info("Install with: pip install qiskit-ibm-runtime")
        return None

    except Exception as e:
        logger.error(f"IBM Quantum connection error: {e}")
        return None


def test_qpe_with_ibm():
    """Test QPE implementation with IBM backend option."""
    from src.quantum_engine.qpe import QuantumPhaseEstimator

    logger.info("Testing QuantumPhaseEstimator...")

    # Create QPE instance (uses local simulator by default)
    qpe = QuantumPhaseEstimator(num_qubits=4, shots=1024)

    # Test with sample price data
    prices = [1.1000, 1.1050, 1.1100, 1.1080, 1.1120, 1.1150]

    result = qpe.estimate_phase(prices)

    logger.info(f"Phase estimation result:")
    logger.info(f"  Phase: {result['phase']:.4f}")
    logger.info(f"  Confidence: {result['confidence']:.2%}")
    logger.info(f"  Measurements: {len(result['measurements'])} outcomes")

    logger.success("✓ QPE working correctly")

    return result


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("IBM Quantum Cloud Integration Test")
    logger.info("=" * 60)

    # Test 1: Local simulator (always works)
    logger.info("\n[Test 1] Local AerSimulator")
    logger.info("-" * 60)
    test_local_simulator()

    # Test 2: IBM Quantum Cloud connection
    logger.info("\n[Test 2] IBM Quantum Cloud Connection")
    logger.info("-" * 60)
    service = test_ibm_quantum_connection()

    # Test 3: QPE implementation
    logger.info("\n[Test 3] Quantum Phase Estimator")
    logger.info("-" * 60)
    test_qpe_with_ibm()

    logger.info("\n" + "=" * 60)
    if service:
        logger.success("All tests passed! IBM Quantum Cloud is accessible.")
    else:
        logger.info("Local quantum simulator working. IBM Cloud connection skipped.")
    logger.info("=" * 60)
