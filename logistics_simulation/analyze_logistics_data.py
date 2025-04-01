#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logistics Simulation Data Analysis Main Script

This script combines the data importer and analyzer to provide a complete
workflow for analyzing logistics simulation data.
"""

import argparse
import os
from pathlib import Path
from data_importer import import_csv_data, import_excel_data, import_json_data, create_sample_data_files
from simulation_data import LogisticsSimulationAnalyzer


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze logistics simulation data')
    
    # Input data options
    input_group = parser.add_argument_group('Input Data')
    input_group.add_argument('--sim-data', type=str, help='Path to simulation data file')
    input_group.add_argument('--reservation-data', type=str, help='Path to reservation data file')
    input_group.add_argument('--combined-data', type=str, help='Path to combined data file (Excel or JSON)')
    input_group.add_argument('--format', type=str, choices=['csv', 'excel', 'json'], 
                            help='Format of the input data files')
    input_group.add_argument('--sim-sheet', type=str, default='SimulationData',
                            help='Sheet name for simulation data in Excel file')
    input_group.add_argument('--res-sheet', type=str, default='ReservationData',
                            help='Sheet name for reservation data in Excel file')
    input_group.add_argument('--create-sample', action='store_true',
                            help='Create sample data files and use them for analysis')
    
    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('--output-dir', type=str, default='results',
                             help='Directory to save analysis results and visualizations')
    output_group.add_argument('--analysis-file', type=str, default='analysis_results.json',
                             help='Filename for the analysis results JSON file')
    output_group.add_argument('--no-visualizations', action='store_true',
                             help='Skip creating visualizations')
    
    return parser.parse_args()


def main():
    """Main function to run the analysis workflow."""
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize the analyzer
    analyzer = LogisticsSimulationAnalyzer()
    
    # Handle input data
    if args.create_sample:
        print("Creating and using sample data files...")
        sim_data_path, reservation_data_path = create_sample_data_files()
        analyzer.load_data(sim_data_path, reservation_data_path)
    
    elif args.combined_data:
        print(f"Loading combined data from {args.combined_data}...")
        if args.format == 'excel' or args.combined_data.endswith(('.xlsx', '.xls')):
            # Load from Excel file
            sim_data = import_excel_data(args.combined_data, sheet_name=args.sim_sheet)
            res_data = import_excel_data(args.combined_data, sheet_name=args.res_sheet)
            analyzer.sim_data = sim_data
            analyzer.reservation_data = res_data
        
        elif args.format == 'json' or args.combined_data.endswith('.json'):
            # Load from JSON file
            sim_data = import_json_data(args.combined_data, record_path='simulation_data')
            res_data = import_json_data(args.combined_data, record_path='reservation_data')
            analyzer.sim_data = sim_data
            analyzer.reservation_data = res_data
        
        else:
            print("Error: Unknown format for combined data file. Use --format to specify.")
            return
    
    elif args.sim_data and args.reservation_data:
        print(f"Loading simulation data from {args.sim_data}...")
        print(f"Loading reservation data from {args.reservation_data}...")
        
        if args.format == 'csv' or (args.sim_data.endswith('.csv') and args.reservation_data.endswith('.csv')):
            # Load from CSV files
            sim_data = import_csv_data(args.sim_data)
            res_data = import_csv_data(args.reservation_data)
            analyzer.sim_data = sim_data
            analyzer.reservation_data = res_data
        
        elif args.format == 'excel' or (args.sim_data.endswith(('.xlsx', '.xls')) and args.reservation_data.endswith(('.xlsx', '.xls'))):
            # Load from Excel files
            sim_data = import_excel_data(args.sim_data)
            res_data = import_excel_data(args.reservation_data)
            analyzer.sim_data = sim_data
            analyzer.reservation_data = res_data
        
        else:
            print("Error: Unknown format for data files. Use --format to specify.")
            return
    
    else:
        print("Error: No input data specified. Use --sim-data and --reservation-data, --combined-data, or --create-sample.")
        return
    
    # Perform analysis
    print("Analyzing data...")
    analysis_results = analyzer.analyze_data()
    
    # Save analysis results
    analysis_file = output_dir / args.analysis_file
    print(f"Saving analysis results to {analysis_file}...")
    analyzer.export_analysis(str(analysis_file))
    
    # Create visualizations
    if not args.no_visualizations:
        vis_dir = output_dir / 'visualizations'
        print(f"Creating visualizations in {vis_dir}...")
        saved_files = analyzer.visualize_data(str(vis_dir))
        print(f"Created {len(saved_files)} visualization files.")
    
    print("Analysis complete!")


if __name__ == "__main__":
    main()
