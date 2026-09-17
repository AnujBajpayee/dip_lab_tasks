"""
Shannon-Fano & Huffman Image Entropy Coding Suite
=================================================
Lossless data compression algorithms operating on image pixel intensity distributions:
1. Probability & Entropy Profiler: H(X) = -sum(p_i * log2(p_i))
2. Shannon-Fano Prefix-Free Codebook Generator
3. Huffman Optimal Prefix-Free Tree & Codebook Generator
4. Bitstream Encoding & Exact Lossless Bitstream Decoding
5. Average Length, Coding Efficiency, and Compression Metrics
"""

from __future__ import annotations
import math
import heapq
from typing import List, Tuple, Dict, Any, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# =============================================================================
# 1. Probability & Entropy Computation
# =============================================================================

def compute_symbol_probabilities(image: np.ndarray) -> Dict[int, float]:
    """Computes the empirical probability distribution of intensity levels in an image."""
    flat = image.flatten().astype(np.uint8)
    total_pixels = len(flat)
    if total_pixels == 0:
        return {}

    counts = np.bincount(flat, minlength=256)
    probs: Dict[int, float] = {}
    for symbol, count in enumerate(counts):
        if count > 0:
            probs[int(symbol)] = float(count) / float(total_pixels)
    return probs


def compute_entropy(probabilities: Dict[int, float]) -> float:
    """
    Computes Shannon Information Entropy H(X):
        H(X) = - sum_{i} p_i * log2(p_i)  [bits / pixel]
    """
    h = 0.0
    for p in probabilities.values():
        if p > 0.0:
            h -= p * math.log2(p)
    return float(h)


# =============================================================================
# 2. Shannon-Fano Coding Algorithm
# =============================================================================

def _shannon_fano_recursive(sorted_symbols: List[Tuple[int, float]], prefix: str, codebook: Dict[int, str]) -> None:
    """Recursively splits symbol list into two balanced probability halves."""
    if len(sorted_symbols) == 1:
        codebook[sorted_symbols[0][0]] = prefix if prefix != "" else "0"
        return
    if len(sorted_symbols) == 2:
        codebook[sorted_symbols[0][0]] = prefix + "0"
        codebook[sorted_symbols[1][0]] = prefix + "1"
        return

    # Find split index that minimizes absolute probability difference
    total_p = sum(p for _, p in sorted_symbols)
    running_p = 0.0
    best_diff = float("inf")
    split_idx = 1

    for i in range(len(sorted_symbols) - 1):
        running_p += sorted_symbols[i][1]
        diff = abs(running_p - (total_p - running_p))
        if diff < best_diff:
            best_diff = diff
            split_idx = i + 1

    left = sorted_symbols[:split_idx]
    right = sorted_symbols[split_idx:]

    _shannon_fano_recursive(left, prefix + "0", codebook)
    _shannon_fano_recursive(right, prefix + "1", codebook)


def build_shannon_fano_codebook(probabilities: Dict[int, float]) -> Dict[int, str]:
    """Generates Shannon-Fano prefix-free binary codes."""
    if not probabilities:
        return {}
    # Sort symbols by descending probability
    sorted_symbols = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    codebook: Dict[int, str] = {}
    _shannon_fano_recursive(sorted_symbols, "", codebook)
    return codebook


# =============================================================================
# 3. Huffman Coding Algorithm
# =============================================================================

class HuffmanNode:
    """Binary tree node for Huffman tree construction."""
    def __init__(self, weight: float, symbol: Optional[int] = None, left: Optional[HuffmanNode] = None, right: Optional[HuffmanNode] = None):
        self.weight = weight
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other: HuffmanNode) -> bool:
        return self.weight < other.weight


def build_huffman_codebook(probabilities: Dict[int, float]) -> Dict[int, str]:
    """
    Constructs the optimal Huffman binary prefix tree and returns codebook dictionary.
    """
    if not probabilities:
        return {}
    if len(probabilities) == 1:
        sym = next(iter(probabilities.keys()))
        return {sym: "0"}

    # Initialize priority queue
    heap: List[Tuple[float, int, HuffmanNode]] = []
    counter = 0
    for sym, prob in probabilities.items():
        node = HuffmanNode(prob, symbol=sym)
        heapq.heappush(heap, (prob, counter, node))
        counter += 1

    while len(heap) > 1:
        w1, _, node1 = heapq.heappop(heap)
        w2, _, node2 = heapq.heappop(heap)

        parent = HuffmanNode(w1 + w2, symbol=None, left=node1, right=node2)
        heapq.heappush(heap, (w1 + w2, counter, parent))
        counter += 1

    _, _, root = heapq.heappop(heap)

    # Traverse tree to assign binary prefix codes
    codebook: Dict[int, str] = {}
    def _traverse(curr: Optional[HuffmanNode], prefix: str):
        if curr is None:
            return
        if curr.symbol is not None:
            codebook[curr.symbol] = prefix
            return
        _traverse(curr.left, prefix + "0")
        _traverse(curr.right, prefix + "1")

    _traverse(root, "")
    return codebook


# =============================================================================
# 4. Encoding, Decoding & Verification
# =============================================================================

def encode_image(image: np.ndarray, codebook: Dict[int, str]) -> Tuple[str, Tuple[int, int]]:
    """Encodes a 2D image array into a binary bitstring using the provided codebook."""
    flat = image.flatten().astype(np.uint8)
    bitstring = "".join(codebook[int(pixel)] for pixel in flat)
    return bitstring, image.shape


def decode_image(bitstring: str, codebook: Dict[int, str], shape: Tuple[int, int]) -> np.ndarray:
    """Decodes a binary bitstring back into a 2D image array with exact lossless fidelity."""
    reverse_map = {code: sym for sym, code in codebook.items()}
    decoded_symbols = []
    current_code = ""

    for bit in bitstring:
        current_code += bit
        if current_code in reverse_map:
            decoded_symbols.append(reverse_map[current_code])
            current_code = ""

    return np.array(decoded_symbols, dtype=np.uint8).reshape(shape)


# =============================================================================
# 5. Coding Efficiency & Compression Metrics
# =============================================================================

def compute_coding_metrics(
    probabilities: Dict[int, float],
    codebook: Dict[int, str]
) -> Dict[str, float]:
    """
    Computes performance metrics:
    - Average Code Length: L_avg = sum(p_i * l_i)
    - Information Entropy: H(X)
    - Coding Efficiency: eta = (H(X) / L_avg) * 100%
    - Redundancy: R = L_avg - H(X)
    - Compression Ratio: CR = 8.0 / L_avg
    """
    h_x = compute_entropy(probabilities)
    l_avg = sum(probabilities[sym] * len(codebook[sym]) for sym in probabilities if sym in codebook)

    efficiency = (h_x / l_avg * 100.0) if l_avg > 0 else 100.0
    redundancy = max(0.0, l_avg - h_x)
    compression_ratio = (8.0 / l_avg) if l_avg > 0 else 1.0
    savings_pct = (1.0 - (l_avg / 8.0)) * 100.0

    return {
        "entropy_bits": round(h_x, 4),
        "avg_length_bits": round(l_avg, 4),
        "efficiency_pct": round(efficiency, 2),
        "redundancy_bits": round(redundancy, 4),
        "compression_ratio": round(compression_ratio, 3),
        "savings_pct": round(savings_pct, 2),
    }
