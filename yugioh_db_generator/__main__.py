#!/usr/bin/env python3
"""Command-line entry point for the Yu-Gi-Oh! Card Database Generator."""

import sys
from yugioh_db_generator.cli.parser import create_parser
from yugioh_db_generator.core.card_database import CardDatabaseGenerator
from yugioh_db_generator.utils.logging_utils import setup_logging
from yugioh_db_generator.utils.file_utils import read_deck_list


def main():
    """Main entry point for the command-line interface."""
    # Set up logging
    logger = setup_logging()
    
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Read the deck list
        if args.input:
            logger.info(f"Reading deck list from: {args.input}")
            deck_list = read_deck_list(args.input)
        else:
            logger.info("No input file provided. Using example deck list.")
            from yugioh_db_generator.utils.file_utils import get_default_deck_list
            deck_list = get_default_deck_list()
        
        if not deck_list:
            logger.error("No cards found in the deck list. Exiting.")
            return 1
            
        logger.info(f"Processing {len(deck_list)} cards...")
        
        # Initialize the generator
        generator = CardDatabaseGenerator(
            output_file=args.output,
            output_format=args.format,
            max_workers=args.threads
        )
        
        # Generate the database
        generator.generate_database(deck_list)
        
        # Save name corrections if requested
        if args.corrections:
            corrections = generator.get_name_corrections()
            if corrections:
                from yugioh_db_generator.utils.file_utils import write_corrections
                write_corrections(corrections, args.corrections)
                logger.info(f"Name corrections saved to: {args.corrections}")
                
        logger.info("Database generation completed successfully.")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        return 130
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
