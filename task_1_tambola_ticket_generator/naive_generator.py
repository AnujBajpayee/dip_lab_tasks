"""
Naive Binary Mask Generator & Empirical Failure Analysis
=========================================================
This module models the initial naive approach to Tambola ticket generation:
generating a 3x9 grid populated purely by binary (0/1) masks via uniform
random selection, and profiles why this approach suffers from significant
rejection rates and combinatorial bottlenecks.
"""

from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class NaiveSimulationStats:
    total_trials: int
    successful_trials: int
    failed_empty_column: int
    success_rate_percent: float
    rejection_rate_percent: float
    average_attempts_until_success: float
    elapsed_seconds: float


def generate_naive_binary_mask(rng: Optional[random.Random] = None) -> List[List[int]]:
    """
    Generates a 3x9 binary mask using the naive row-wise random selection approach.
    
    In each row of 9 columns, exactly 5 columns are randomly chosen to be 1 (active)
    and 4 are chosen to be 0 (blank).
    
    Total active cells = 15.
    Row sums = exactly 5.
    """
    r = rng if rng is not None else random.Random()
    mask = []
    for _ in range(3):
        row = [0] * 9
        chosen_indices = r.sample(range(9), 5)
        for idx in chosen_indices:
            row[idx] = 1
        mask.append(row)
    return mask


def is_valid_binary_mask(mask: List[List[int]]) -> Tuple[bool, str]:
    """
    Validates whether a 3x9 binary mask satisfies Tambola structural constraints.
    """
    if len(mask) != 3 or any(len(row) != 9 for row in mask):
        return False, "Invalid matrix dimensions. Expected 3x9."
        
    for r_idx, row in enumerate(mask):
        if sum(row) != 5:
            return False, f"Row {r_idx} does not have exactly 5 active cells (found {sum(row)})."
            
    for c_idx in range(9):
        col_sum = sum(mask[r_idx][c_idx] for r_idx in range(3))
        if col_sum == 0:
            return False, f"Column {c_idx} is empty (0 numbers)."
        if col_sum > 3:
            return False, f"Column {c_idx} exceeds maximum capacity of 3 (found {col_sum})."
            
    return True, "Valid"


def simulate_naive_generation(
    num_trials: int = 10000,
    seed: Optional[int] = None
) -> NaiveSimulationStats:
    """
    Runs an empirical Monte-Carlo simulation to measure the failure rate of the naive
    0/1 binary array generator due to column starvation.
    """
    rng = random.Random(seed)
    start_time = time.perf_counter()
    
    successes = 0
    empty_col_failures = 0
    attempts_for_first_100: List[int] = []
    
    current_attempts = 0
    for _ in range(num_trials):
        mask = generate_naive_binary_mask(rng)
        valid, _ = is_valid_binary_mask(mask)
        current_attempts += 1
        
        if valid:
            successes += 1
            if len(attempts_for_first_100) < 100:
                attempts_for_first_100.append(current_attempts)
                current_attempts = 0
        else:
            empty_col_failures += 1
            
    elapsed = time.perf_counter() - start_time
    
    success_rate = (successes / num_trials) * 100.0 if num_trials > 0 else 0.0
    rejection_rate = 100.0 - success_rate
    avg_attempts = (
        sum(attempts_for_first_100) / len(attempts_for_first_100)
        if attempts_for_first_100 else (1.0 / (successes / num_trials) if successes > 0 else float('inf'))
    )
    
    return NaiveSimulationStats(
        total_trials=num_trials,
        successful_trials=successes,
        failed_empty_column=empty_col_failures,
        success_rate_percent=round(success_rate, 2),
        rejection_rate_percent=round(rejection_rate, 2),
        average_attempts_until_success=round(avg_attempts, 2),
        elapsed_seconds=round(elapsed, 4)
    )
