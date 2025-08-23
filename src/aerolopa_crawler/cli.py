"""Command-line interface for the AeroLOPA crawler."""

import argparse
import logging
import sys
from typing import List, Optional

from .config import load_config
from .aerolopa_crawler import AerolopaCrawler
from .airlines import get_supported_iata_codes


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def list_supported_airlines() -> None:
    """List all supported airlines."""
    from .airlines import get_all_airlines
    
    airlines = get_all_airlines()
    print("\nSupported Airlines:")
    print("-" * 50)
    
    for iata, (chinese_name, english_name) in sorted(airlines.items()):
        print(f"{iata:3} | {chinese_name:20} | {english_name}")
    
    print(f"\nTotal: {len(airlines)} airlines supported")


def validate_airline_codes(airline_codes: List[str]) -> List[str]:
    """Validate airline IATA codes.
    
    Args:
        airline_codes: List of IATA codes to validate
        
    Returns:
        List of valid IATA codes
    """
    supported_codes = set(get_supported_iata_codes())
    valid_codes = []
    invalid_codes = []
    
    for code in airline_codes:
        code = code.upper().strip()
        if code in supported_codes:
            valid_codes.append(code)
        else:
            invalid_codes.append(code)
    
    if invalid_codes:
        print(f"Warning: Unsupported airline codes: {', '.join(invalid_codes)}", file=sys.stderr)
        print("Use --list-airlines to see supported airlines", file=sys.stderr)
    
    return valid_codes


def parse_airline_codes(codes_input: str) -> List[str]:
    """Parse airline codes from command line input.
    
    Args:
        codes_input: Comma-separated airline codes
        
    Returns:
        List of airline codes
    """
    if not codes_input:
        return []
    
    codes = [code.strip().upper() for code in codes_input.split(',')]
    return [code for code in codes if code]


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AeroLOPA Seat Map Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --airline CA                    # Crawl Air China seat maps
  %(prog)s --airline "CA,MU,CZ"            # Crawl multiple airlines
  %(prog)s --all-airlines                  # Crawl all supported airlines
  %(prog)s --list-airlines                 # List supported airlines
  %(prog)s --airline CA --verbose          # Enable verbose logging
        """
    )
    
    # Main action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    
    action_group.add_argument(
        "--airline", "-a",
        help="Comma-separated list of airline IATA codes to crawl (e.g., 'CA,MU,CZ')"
    )
    
    action_group.add_argument(
        "--all-airlines",
        action="store_true",
        help="Crawl seat maps for all supported airlines"
    )
    
    action_group.add_argument(
        "--list-airlines",
        action="store_true",
        help="List all supported airlines and exit"
    )
    
    # Optional arguments
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for results (overrides config)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show crawling statistics after completion"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Handle list airlines command
        if args.list_airlines:
            list_supported_airlines()
            return
        
        # Load configuration
        config = load_config()
        
        # Override output directory if specified
        if args.output_dir:
            config.crawler.output_dir = args.output_dir
        
        # Initialize crawler
        crawler = AerolopaCrawler(config)
        
        # Determine which airlines to crawl
        if args.all_airlines:
            print("Starting crawl for all supported airlines...")
            total_processed = crawler.crawl_all_airlines()
            
        elif args.airline:
            airline_codes = parse_airline_codes(args.airline)
            valid_codes = validate_airline_codes(airline_codes)
            
            if not valid_codes:
                print("Error: No valid airline codes provided", file=sys.stderr)
                sys.exit(1)
            
            print(f"Starting crawl for airlines: {', '.join(valid_codes)}")
            
            total_processed = 0
            for airline_code in valid_codes:
                processed = crawler.crawl_airline_seatmaps(airline_code)
                total_processed += processed
        
        # Show results
        print(f"\nCrawl completed successfully!")
        print(f"Total seat maps processed: {total_processed}")
        print(f"Results saved to: {config.crawler.output_dir}")
        
        # Show statistics if requested
        if args.stats:
            stats = crawler.get_crawl_statistics()
            print("\nCrawling Statistics:")
            print("-" * 30)
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        
    except KeyboardInterrupt:
        print("\nCrawl interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Crawl failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

