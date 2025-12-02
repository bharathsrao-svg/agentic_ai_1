"""
Wrapper script to periodically run agent_with_holdings.py
Calls the holdings analysis script at specified intervals
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


def run_holdings_analysis(date: str, min_variation: float = 2.0, data_dir: str = "data"):
    """
    Run agent_with_holdings.py with the specified date
    
    Args:
        date: Date in YYYYMMDD format
        min_variation: Minimum price variation percentage (default: 5.0)
        data_dir: Directory containing EOD holdings JSON files
    
    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = Path(__file__).parent.parent
    agent_script = script_dir / "agent_with_holdings.py"
    
    if not agent_script.exists():
        print(f"[ERROR] agent_with_holdings.py not found at: {agent_script}")
        return False
    
    # Build command
    cmd = [
        sys.executable,
        str(agent_script),
       # "--date", date,
        "--min-variation", str(min_variation),
      #  "--data-dir", data_dir
    ]
    
    print(f"\n{'='*80}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running holdings analysis...")
    print(f"{'='*80}")
    
    try:
        # Run the script
        result = subprocess.run(
            cmd,
            cwd=str(script_dir),
            check=False,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Analysis completed successfully")
            return True
        else:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Analysis completed with errors (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to run holdings analysis: {e}")
        return False


def schedule_analysis(date: str, frequency_minutes: int, min_variation: float = 2.0, 
                     data_dir: str = "data", max_iterations: int = None):
    """
    Schedule periodic execution of holdings analysis
    
    Args:
        date: Date in YYYYMMDD format
        frequency_minutes: How often to run (in minutes)
        min_variation: Minimum price variation percentage
        data_dir: Directory containing EOD holdings JSON files
        max_iterations: Maximum number of iterations (None for infinite)
    """
    print("=" * 80)
    print("Holdings Analysis Scheduler")
    print("=" * 80)
   # print(f"Date: {date}")
    print(f"Frequency: Every {frequency_minutes} minute(s)")
    print(f"Min Variation: {min_variation}%")
    if max_iterations:
        print(f"Max Iterations: {max_iterations}")
    else:
        print("Max Iterations: Infinite (Press Ctrl+C to stop)")
    print("=" * 80)
    
    iteration = 0
    frequency_seconds = frequency_minutes * 60
    
    try:
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Run the analysis
            success = run_holdings_analysis(date, min_variation, data_dir)
            
            # Check if we've reached max iterations
            if max_iterations and iteration >= max_iterations:
                print(f"\n[INFO] Reached maximum iterations ({max_iterations}). Stopping.")
                break
            
            # Wait for next execution (unless this was the last iteration)
            if not max_iterations or iteration < max_iterations:
                next_run = datetime.now().timestamp() + frequency_seconds
                next_run_str = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[INFO] Next run scheduled at: {next_run_str}")
                print(f"[INFO] Waiting {frequency_minutes} minute(s)...")
                time.sleep(frequency_seconds)
            
    except KeyboardInterrupt:
        print(f"\n\n[INFO] Scheduler stopped by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[INFO] Completed {iteration} iteration(s)")
    except Exception as e:
        print(f"\n[ERROR] Scheduler error: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description='Schedule periodic execution of holdings price variation analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run every 30 minutes
  python scripts/schedule_holdings_analysis.py --date 20251124 --frequency 30
  
  # Run every 5 minutes, 10 times
  python scripts/schedule_holdings_analysis.py --date 20251124 --frequency 5 --max-iterations 10
  
  # Run every hour with custom variation threshold
  python scripts/schedule_holdings_analysis.py --date 20251124 --frequency 60 --min-variation 3.0
        """
    )
    
    parser.add_argument(
        '--date',
        type=str,
        required=False,
        default=None,
        help='Date in YYYYMMDD format for yesterday holdings file (e.g., 20251124)'
    )
    parser.add_argument(
        '--frequency',
        type=int,
        required=True,
        help='Frequency in minutes (how often to run the analysis)'
    )
    parser.add_argument(
        '--min-variation',
        type=float,
        default=5.0,
        help='Minimum price variation percentage to filter (default: 5.0)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing EOD holdings JSON files (default: data)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of iterations to run (default: infinite, run until stopped)'
    )
    
    args = parser.parse_args()
    
    # Validate frequency
    if args.frequency < 1:
        print("[ERROR] Frequency must be at least 1 minute")
        sys.exit(1)
    
    # Validate date format (basic check)
   # if len(args.date) != 8 or not args.date.isdigit():
    #    print("[ERROR] Date must be in YYYYMMDD format (e.g., 20251124)")
     #   sys.exit(1)
    
    # Start scheduling
    schedule_analysis(
        date=args.date,
        frequency_minutes=args.frequency,
        min_variation=args.min_variation,
        data_dir=args.data_dir,
        max_iterations=args.max_iterations
    )


if __name__ == "__main__":
    main()

