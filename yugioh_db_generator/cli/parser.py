"""Command-line argument parser for the Yu-Gi-Oh! Card Database Generator."""

import argparse
import os
import multiprocessing


def create_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate a comprehensive Yu-Gi-Oh! card database from a deck list',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input/output options
    parser.add_argument(
        '--input', '-i',
        help='Path to the input file containing card names (one per line)'
    )
    
    parser.add_argument(
        '--output', '-o', 
        default='yugioh_card_database.md',
        help='Path to the output file for the generated database'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json', 'csv', 'text'],
        default='markdown',
        help='Output format for the database'
    )
    
    parser.add_argument(
        '--corrections', '-c',
        help='Path to save a list of corrected card names'
    )
    
    # Performance options
    parser.add_argument(
        '--threads', '-t',
        type=int,
        default=max(1, multiprocessing.cpu_count() // 2),
        help='Number of threads for parallel processing'
    )
    
    # Cache options
    parser.add_argument(
        '--cache-dir',
        default=os.path.join(os.path.expanduser('~'), '.yugioh_db_generator', 'cache'),
        help='Directory to store cached card data'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable using cached data (always fetch from API)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear the cache before running'
    )
    
    # Advanced options
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.7,
        help='Minimum similarity score for fuzzy matching (0.0-1.0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='Increase verbosity (can be used multiple times)'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show the version and exit'
    )
    
    return parser
