"""
Tambola (Housie) Core Engine & Constraint-Satisfaction Generator
================================================================
Implements production-grade Tambola ticket and strip generation adhering to all
international Housie / Tambola mathematical rules and structural invariants.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set, Any

# Column Ranges according to official Tambola rules:
# Col 0: 1-9   (9 numbers)
# Col 1: 10-19 (10 numbers)
# Col 2: 20-29 (10 numbers)
# Col 3: 30-39 (10 numbers)
# Col 4: 40-49 (10 numbers)
# Col 5: 50-59 (10 numbers)
# Col 6: 60-69 (10 numbers)
# Col 7: 70-79 (10 numbers)
# Col 8: 80-90 (11 numbers)
COLUMN_RANGES: List[Tuple[int, int]] = [
    (1, 9),
    (10, 19),
    (20, 29),
    (30, 39),
    (40, 49),
    (50, 59),
    (60, 69),
    (70, 79),
    (80, 90),
]


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.is_valid


@dataclass
class TambolaTicket:
    """
    Represents a standard 3x9 Tambola Ticket.
    Empty cells are represented by 0. Active numbers are integers >= 1.
    """
    grid: List[List[int]]
    ticket_id: Optional[str] = None

    def __post_init__(self):
        if len(self.grid) != 3 or any(len(row) != 9 for row in self.grid):
            raise ValueError(f"Invalid grid dimensions. Must be 3x9, got {len(self.grid)}x{len(self.grid[0]) if self.grid else 0}.")

    @property
    def rows(self) -> List[List[int]]:
        return self.grid

    def get_numbers(self) -> List[int]:
        """Returns all non-zero numbers present on this ticket."""
        return [num for row in self.grid for num in row if num > 0]

    def get_column_numbers(self, col_idx: int) -> List[int]:
        """Returns the non-zero numbers in a specific column, ordered top to bottom."""
        if not (0 <= col_idx < 9):
            raise IndexError(f"Column index must be between 0 and 8, got {col_idx}.")
        return [self.grid[r][col_idx] for r in range(3) if self.grid[r][col_idx] > 0]

    def to_matrix(self) -> List[List[int]]:
        """Returns a deep copy of the 3x9 integer grid."""
        return [row[:] for row in self.grid]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the ticket to a structured dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "grid": self.to_matrix(),
            "total_numbers": len(self.get_numbers()),
            "numbers_list": sorted(self.get_numbers()),
            "is_valid": validate_ticket(self).is_valid,
        }


@dataclass
class TambolaStrip:
    """
    Represents a full strip of 6 Tambola tickets containing all numbers 1-90 exactly once.
    """
    tickets: List[TambolaTicket]
    strip_id: Optional[str] = None

    def __post_init__(self):
        if len(self.tickets) != 6:
            raise ValueError(f"A Tambola strip must contain exactly 6 tickets, got {len(self.tickets)}.")

    def get_all_numbers(self) -> List[int]:
        """Returns all numbers across all 6 tickets."""
        nums = []
        for t in self.tickets:
            nums.extend(t.get_numbers())
        return nums

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strip_id": self.strip_id,
            "tickets": [t.to_dict() for t in self.tickets],
            "total_numbers": len(self.get_all_numbers()),
            "is_valid": validate_strip(self).is_valid,
        }


def validate_ticket(ticket: TambolaTicket | List[List[int]]) -> ValidationResult:
    """
    Exhaustively validates a single Tambola ticket against all rules:
    1. Dimensions must be 3 rows x 9 columns.
    2. Total numbers must be exactly 15 (12 empty cells / 0s).
    3. Each row must have exactly 5 numbers.
    4. Each column must have between 1 and 3 numbers.
    5. Numbers in each column must belong to the proper numerical range.
    6. Numbers in each column must be strictly ascending from top to bottom.
    7. No duplicate numbers may exist on the ticket.
    """
    errors: List[str] = []
    
    grid = ticket.grid if isinstance(ticket, TambolaTicket) else ticket
    
    # 1. Dimensions check
    if not isinstance(grid, list) or len(grid) != 3:
        return ValidationResult(is_valid=False, errors=[f"Ticket must have exactly 3 rows. Found {len(grid) if isinstance(grid, list) else type(grid)}."])
    for r_idx, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != 9:
            return ValidationResult(is_valid=False, errors=[f"Row {r_idx} must have exactly 9 columns. Found {len(row) if isinstance(row, list) else type(row)}."])

    # Extract all numbers
    all_numbers: List[int] = []
    
    # 2 & 3. Row check
    for r_idx, row in enumerate(grid):
        row_numbers = [val for val in row if isinstance(val, int) and val > 0]
        all_numbers.extend(row_numbers)
        if len(row_numbers) != 5:
            errors.append(f"Row {r_idx} does not have exactly 5 numbers (found {len(row_numbers)}).")

    # Check total count
    if len(all_numbers) != 15:
        errors.append(f"Ticket must contain exactly 15 numbers (found {len(all_numbers)}).")

    # 7. Duplicate check
    seen: Set[int] = set()
    for num in all_numbers:
        if num in seen:
            errors.append(f"Duplicate number {num} found on ticket.")
        seen.add(num)

    # 4, 5, 6. Column checks
    for col_idx in range(9):
        col_vals = [grid[r_idx][col_idx] for r_idx in range(3) if grid[r_idx][col_idx] > 0]
        
        # Column count constraint
        if len(col_vals) == 0:
            errors.append(f"Column {col_idx} is empty (minimum 1 number required).")
        elif len(col_vals) > 3:
            errors.append(f"Column {col_idx} has {len(col_vals)} numbers (maximum 3 allowed).")
            
        # Range constraints
        min_val, max_val = COLUMN_RANGES[col_idx]
        for val in col_vals:
            if not (min_val <= val <= max_val):
                errors.append(f"Number {val} in column {col_idx} is outside valid range [{min_val}, {max_val}].")
                
        # Ascending order check
        for i in range(len(col_vals) - 1):
            if col_vals[i] >= col_vals[i + 1]:
                errors.append(
                    f"Column {col_idx} numbers are not in strictly ascending order: {col_vals[i]} >= {col_vals[i+1]}."
                )

    metadata = {
        "number_count": len(all_numbers),
        "numbers": sorted(all_numbers),
        "columns_counts": [len([grid[r][c] for r in range(3) if grid[r][c] > 0]) for c in range(9)]
    }
    
    return ValidationResult(is_valid=(len(errors) == 0), errors=errors, metadata=metadata)


def validate_strip(strip: TambolaStrip | List[TambolaTicket]) -> ValidationResult:
    """
    Validates a full strip of 6 tickets:
    1. Must contain exactly 6 tickets.
    2. Each individual ticket must pass validate_ticket().
    3. The union of all numbers across all 6 tickets must be exactly {1, 2, ..., 90}.
    """
    errors: List[str] = []
    tickets = strip.tickets if isinstance(strip, TambolaStrip) else strip
    
    if len(tickets) != 6:
        return ValidationResult(is_valid=False, errors=[f"Strip must have exactly 6 tickets (found {len(tickets)})."])
        
    all_numbers: List[int] = []
    for idx, ticket in enumerate(tickets):
        t_res = validate_ticket(ticket)
        if not t_res.is_valid:
            errors.append(f"Ticket #{idx + 1} is invalid: {'; '.join(t_res.errors)}")
        all_numbers.extend(ticket.get_numbers())
        
    if len(all_numbers) != 90:
        errors.append(f"Strip total numbers count is {len(all_numbers)} (expected exactly 90).")
        
    expected_set = set(range(1, 91))
    actual_set = set(all_numbers)
    
    missing = expected_set - actual_set
    if missing:
        errors.append(f"Missing numbers in strip: {sorted(list(missing))}")
        
    if len(actual_set) != len(all_numbers):
        duplicates = [x for x in actual_set if all_numbers.count(x) > 1]
        errors.append(f"Duplicate numbers across strip: {sorted(duplicates)}")
        
    return ValidationResult(
        is_valid=(len(errors) == 0),
        errors=errors,
        metadata={"total_numbers": len(all_numbers), "unique_numbers": len(actual_set)}
    )


def _solve_binary_grid_bipartite(
    col_counts: List[int],
    rng: random.Random
) -> Optional[List[List[int]]]:
    """
    Solves for a 3x9 binary grid (0s and 1s) such that:
    - Each row sum is exactly 5.
    - Each column sum matches col_counts[c].
    - Grid values are binary (0 or 1).
    """
    grid = [[0] * 9 for _ in range(3)]
    row_capacities = [5, 5, 5]
    
    col_indices = list(range(9))
    rng.shuffle(col_indices)
    col_indices.sort(key=lambda c: col_counts[c], reverse=True)
    
    def backtrack(col_ptr: int) -> bool:
        if col_ptr == 9:
            return all(rc == 0 for rc in row_capacities)
            
        c = col_indices[col_ptr]
        k = col_counts[c]
        
        if k == 3:
            if all(row_capacities[r] >= 1 for r in range(3)):
                for r in range(3):
                    grid[r][c] = 1
                    row_capacities[r] -= 1
                if backtrack(col_ptr + 1):
                    return True
                for r in range(3):
                    grid[r][c] = 0
                    row_capacities[r] += 1
            return False
            
        elif k == 2:
            candidate_pairs = [(0, 1), (0, 2), (1, 2)]
            rng.shuffle(candidate_pairs)
            for r1, r2 in candidate_pairs:
                if row_capacities[r1] > 0 and row_capacities[r2] > 0:
                    grid[r1][c] = 1
                    grid[r2][c] = 1
                    row_capacities[r1] -= 1
                    row_capacities[r2] -= 1
                    if backtrack(col_ptr + 1):
                        return True
                    grid[r1][c] = 0
                    grid[r2][c] = 0
                    row_capacities[r1] += 1
                    row_capacities[r2] += 1
            return False
            
        elif k == 1:
            candidate_rows = [0, 1, 2]
            candidate_rows.sort(key=lambda r: row_capacities[r], reverse=True)
            for r in candidate_rows:
                if row_capacities[r] > 0:
                    grid[r][c] = 1
                    row_capacities[r] -= 1
                    if backtrack(col_ptr + 1):
                        return True
                    grid[r][c] = 0
                    row_capacities[r] += 1
            return False
            
        return False

    if backtrack(0):
        return grid
    return None


def generate_ticket(
    seed: Optional[int] = None,
    ticket_id: Optional[str] = None
) -> TambolaTicket:
    """
    Generates a guaranteed valid single Tambola ticket using CSP bipartite allocation.
    """
    rng = random.Random(seed)
    
    valid_dist_templates = [
        [2, 2, 2, 2, 2, 2, 1, 1, 1],
        [3, 2, 2, 2, 2, 1, 1, 1, 1],
    ]
    
    for _ in range(50):
        template = rng.choice(valid_dist_templates)[:]
        rng.shuffle(template)
        
        binary_grid = _solve_binary_grid_bipartite(template, rng)
        if binary_grid is not None:
            final_grid = [[0] * 9 for _ in range(3)]
            for col_idx in range(9):
                count = template[col_idx]
                min_val, max_val = COLUMN_RANGES[col_idx]
                pool = list(range(min_val, max_val + 1))
                sampled_numbers = sorted(rng.sample(pool, count))
                
                s_idx = 0
                for r_idx in range(3):
                    if binary_grid[r_idx][col_idx] == 1:
                        final_grid[r_idx][col_idx] = sampled_numbers[s_idx]
                        s_idx += 1
                        
            ticket = TambolaTicket(grid=final_grid, ticket_id=ticket_id or f"TKT-{rng.randint(1000, 9999)}")
            assert validate_ticket(ticket).is_valid
            return ticket
            
    raise RuntimeError("Failed to generate valid Tambola ticket.")


def generate_strip(
    seed: Optional[int] = None,
    strip_id: Optional[str] = None
) -> TambolaStrip:
    """
    Generates a complete Tambola strip of 6 tickets containing all numbers 1-90 exactly once.
    """
    rng = random.Random(seed)
    
    for attempt in range(100):
        col_counts_per_ticket = [[0] * 9 for _ in range(6)]
        
        # Col 0: three 2s, three 1s (9 total)
        c0 = [2, 2, 2, 1, 1, 1]
        rng.shuffle(c0)
        for t in range(6):
            col_counts_per_ticket[t][0] = c0[t]
            
        # Col 1..7: four 2s, two 1s each (10 total each)
        for c in range(1, 8):
            cc = [2, 2, 2, 2, 1, 1]
            rng.shuffle(cc)
            for t in range(6):
                col_counts_per_ticket[t][c] = cc[t]
                
        # Col 8: five 2s, one 1 (11 total)
        c8 = [2, 2, 2, 2, 2, 1]
        rng.shuffle(c8)
        for t in range(6):
            col_counts_per_ticket[t][8] = c8[t]
            
        # Balance ticket sums to exactly 15 each
        ticket_sums = [sum(col_counts_per_ticket[t]) for t in range(6)]
        if any(ts != 15 for ts in ticket_sums):
            for _ in range(500):
                t_over = [t for t in range(6) if sum(col_counts_per_ticket[t]) > 15]
                t_under = [t for t in range(6) if sum(col_counts_per_ticket[t]) < 15]
                if not t_over or not t_under:
                    break
                t1 = rng.choice(t_over)
                t2 = rng.choice(t_under)
                
                valid_cols = [c for c in range(9) if col_counts_per_ticket[t1][c] == 2 and col_counts_per_ticket[t2][c] == 1]
                if valid_cols:
                    chosen_c = rng.choice(valid_cols)
                    col_counts_per_ticket[t1][chosen_c] = 1
                    col_counts_per_ticket[t2][chosen_c] = 2
                    
        if not all(sum(col_counts_per_ticket[t]) == 15 for t in range(6)):
            continue
            
        # Solve binary grids
        binary_grids = []
        possible = True
        for t in range(6):
            b_grid = _solve_binary_grid_bipartite(col_counts_per_ticket[t], rng)
            if b_grid is None:
                possible = False
                break
            binary_grids.append(b_grid)
            
        if not possible:
            continue
            
        # Distribute numbers 1..90
        tickets_list = []
        for c in range(9):
            min_val, max_val = COLUMN_RANGES[c]
            full_col_pool = list(range(min_val, max_val + 1))
            rng.shuffle(full_col_pool)
            
            pool_ptr = 0
            for t in range(6):
                count = col_counts_per_ticket[t][c]
                t_sampled = full_col_pool[pool_ptr : pool_ptr + count]
                pool_ptr += count
                t_sampled.sort()
                
                if len(tickets_list) <= t:
                    tickets_list.append([[0] * 9 for _ in range(3)])
                    
                s_idx = 0
                for r in range(3):
                    if binary_grids[t][r][c] == 1:
                        tickets_list[t][r][c] = t_sampled[s_idx]
                        s_idx += 1
                        
        strip_tickets = [
            TambolaTicket(grid=tickets_list[t], ticket_id=f"STRIP-{strip_id or 1}-TKT-{t+1}")
            for t in range(6)
        ]
        
        strip = TambolaStrip(tickets=strip_tickets, strip_id=strip_id or f"STRIP-{rng.randint(1000, 9999)}")
        v_res = validate_strip(strip)
        if v_res.is_valid:
            return strip
            
    raise RuntimeError("Failed to generate complete valid Tambola strip.")
