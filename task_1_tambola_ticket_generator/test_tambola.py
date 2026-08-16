"""
Unit Tests for Task 1: Tambola Ticket & Strip Generation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_1_tambola_ticket_generator.generator import (
    TambolaTicket,
    TambolaStrip,
    generate_ticket,
    generate_strip,
    validate_ticket,
    validate_strip,
    COLUMN_RANGES,
)
from task_1_tambola_ticket_generator.naive_generator import (
    generate_naive_binary_mask,
    is_valid_binary_mask,
    simulate_naive_generation,
)
from task_1_tambola_ticket_generator.visualizer import (
    ticket_to_ascii,
    ticket_to_markdown,
    ticket_to_svg,
    ticket_to_png,
    strip_to_ascii,
    strip_to_markdown,
)


def test_single_ticket_generation_invariants():
    for i in range(50):
        ticket = generate_ticket(seed=1000 + i)
        v_res = validate_ticket(ticket)
        assert v_res.is_valid, f"Ticket #{i} failed: {v_res.errors}"
        
        assert len(ticket.grid) == 3
        for row in ticket.grid:
            assert len(row) == 9
            assert len([x for x in row if x > 0]) == 5
            
        all_nums = ticket.get_numbers()
        assert len(all_nums) == 15
        assert len(set(all_nums)) == 15
        
        for c in range(9):
            col_nums = ticket.get_column_numbers(c)
            assert 1 <= len(col_nums) <= 3
            min_v, max_v = COLUMN_RANGES[c]
            for val in col_nums:
                assert min_v <= val <= max_v
            for k in range(len(col_nums) - 1):
                assert col_nums[k] < col_nums[k + 1]


def test_full_strip_generation():
    for s_idx in range(10):
        strip = generate_strip(seed=5000 + s_idx)
        v_res = validate_strip(strip)
        assert v_res.is_valid, f"Strip #{s_idx} failed: {v_res.errors}"
        assert len(strip.tickets) == 6
        all_nums = strip.get_all_numbers()
        assert len(all_nums) == 90
        assert set(all_nums) == set(range(1, 91))


def test_validator_edge_cases():
    assert not validate_ticket([[1, 2, 3]]).is_valid
    
    valid_ticket = generate_ticket(seed=42)
    assert validate_ticket(valid_ticket).is_valid
    
    # Bad row sum
    bad_grid = [row[:] for row in valid_ticket.grid]
    empty_col = next(c for c in range(9) if bad_grid[0][c] == 0)
    bad_grid[0][empty_col] = COLUMN_RANGES[empty_col][0]
    assert not validate_ticket(bad_grid).is_valid

    # Out of range
    bad_grid_2 = [row[:] for row in valid_ticket.grid]
    bad_grid_2[0][0] = 99
    assert not validate_ticket(bad_grid_2).is_valid


def test_naive_binary_mask_rejection():
    stats = simulate_naive_generation(num_trials=1000, seed=42)
    assert stats.total_trials == 1000
    assert stats.failed_empty_column > 0
    assert stats.rejection_rate_percent > 15.0


def test_visualizers(tmp_path):
    ticket = generate_ticket(seed=42, ticket_id="TEST-TKT")
    assert "TEST-TKT" in ticket_to_ascii(ticket)
    assert "| Col 1 (1-9) |" in ticket_to_markdown(ticket)
    
    svg_p = str(tmp_path / "t.svg")
    ticket_to_svg(ticket, output_path=svg_p)
    assert Path(svg_p).exists()
    
    png_p = str(tmp_path / "t.png")
    ticket_to_png(ticket, output_path=png_p)
    assert Path(png_p).exists()
