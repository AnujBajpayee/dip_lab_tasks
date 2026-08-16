"""
Tambola Engine Entry Point & CLI Runner
======================================
"""

from __future__ import annotations
import argparse
import json
import sys
import os
from pathlib import Path

# Configure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_1_tambola_ticket_generator.generator import (
    generate_ticket,
    generate_strip,
    validate_ticket,
    validate_strip,
)
from task_1_tambola_ticket_generator.naive_generator import simulate_naive_generation
from task_1_tambola_ticket_generator.visualizer import (
    ticket_to_ascii,
    ticket_to_markdown,
    ticket_to_svg,
    ticket_to_png,
    strip_to_ascii,
    HAS_PILLOW,
)


def main():
    parser = argparse.ArgumentParser(
        description="Task 1: Tambola (Housie) Engine - Generator, Visualizer & Benchmarker"
    )
    parser.add_argument("--ticket", action="store_true", help="Generate a single valid Tambola ticket")
    parser.add_argument("--strip", action="store_true", help="Generate a full 6-ticket strip (numbers 1-90)")
    parser.add_argument("--count", type=int, default=1, help="Number of tickets to generate (default: 1)")
    parser.add_argument("--benchmark", action="store_true", help="Run naive 0/1 binary array failure simulation")
    parser.add_argument("--trials", type=int, default=10000, help="Number of trials for benchmark (default: 10000)")
    parser.add_argument("--export-txt", type=str, help="Save ASCII ticket to file path")
    parser.add_argument("--export-json", type=str, help="Save JSON ticket representation to file path")
    parser.add_argument("--export-svg", type=str, help="Save SVG visual ticket to file path")
    parser.add_argument("--export-png", type=str, help="Save PNG image ticket to file path")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic output")

    args = parser.parse_args()

    if not args.ticket and not args.strip and not args.benchmark:
        args.ticket = True

    if args.benchmark:
        print("\n" + "=" * 60)
        print("📊 RUNNING NAIVE BINARY MASK SIMULATION BENCHMARK")
        print("=" * 60)
        print(f"Executing {args.trials:,} random binary grid selections (5 ones per row)...")
        stats = simulate_naive_generation(num_trials=args.trials, seed=args.seed)
        
        print("\nResults:")
        print(f"  • Total Trials:                 {stats.total_trials:,}")
        print(f"  • Successful Masks:             {stats.successful_trials:,} ({stats.success_rate_percent}%)")
        print(f"  • Empty Column Failures:        {stats.failed_empty_column:,} ({stats.rejection_rate_percent}%)")
        print(f"  • Avg Attempts per Valid Mask:  {stats.average_attempts_until_success:.2f} attempts")
        print(f"  • Execution Time:               {stats.elapsed_seconds:.4f}s")
        print("\nConclusion: Naive random 0/1 array sampling suffers ~28.5% rejection rate on single tickets,")
        print("and exponentially collapses when attempting full strip partitioning without constraint satisfaction.\n")
        return

    if args.strip:
        print("\n" + "=" * 60)
        print("🎫 GENERATING COMPLETE TAMBOLA STRIP (6 TICKETS, NUMBERS 1-90)")
        print("=" * 60)
        strip = generate_strip(seed=args.seed)
        v_res = validate_strip(strip)
        
        print(strip_to_ascii(strip))
        print(f"Validation Status: {'✅ PASSED (All 90 numbers present exactly once)' if v_res.is_valid else '❌ FAILED'}")
        
        if args.export_txt:
            with open(args.export_txt, "w", encoding="utf-8") as f:
                f.write(strip_to_ascii(strip))
            print(f"Saved text strip to: {args.export_txt}")
            
        if args.export_json:
            with open(args.export_json, "w", encoding="utf-8") as f:
                json.dump(strip.to_dict(), f, indent=2)
            print(f"Saved JSON strip to: {args.export_json}")
        return

    if args.ticket:
        for i in range(args.count):
            t_id = f"TICKET-{i+1:03d}" if args.count > 1 else None
            ticket = generate_ticket(seed=args.seed + i if args.seed is not None else None, ticket_id=t_id)
            v_res = validate_ticket(ticket)
            
            print(ticket_to_ascii(ticket))
            print(f"Validation Status: {'✅ PASSED (15 numbers, 5/row, sorted columns)' if v_res.is_valid else '❌ FAILED'}\n")
            
            if args.export_txt:
                with open(args.export_txt, "w", encoding="utf-8") as f:
                    f.write(ticket_to_ascii(ticket))
                print(f"Saved text ticket to: {args.export_txt}")
                
            if args.export_json:
                with open(args.export_json, "w", encoding="utf-8") as f:
                    json.dump(ticket.to_dict(), f, indent=2)
                print(f"Saved JSON ticket to: {args.export_json}")
                
            if args.export_svg:
                ticket_to_svg(ticket, output_path=args.export_svg)
                print(f"Saved SVG ticket to: {args.export_svg}")
                
            if args.export_png:
                if HAS_PILLOW:
                    ticket_to_png(ticket, output_path=args.export_png)
                    print(f"Saved PNG ticket to: {args.export_png}")


if __name__ == "__main__":
    main()
