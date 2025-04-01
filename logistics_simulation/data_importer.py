#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Importer for Logistics Simulation Analysis

This script provides utilities to import and convert data from various formats
to the format expected by the LogisticsSimulationAnalyzer.
"""

import pandas as pd
import os
import csv
import json
from pathlib import Path


def detect_delimiter(file_path, num_lines=5):
    """
    Detect the delimiter used in a text file.
    
    Args:
        file_path (str): Path to the file
        num_lines (int): Number of lines to check
    
    Returns:
        str: Detected delimiter
    """
    with open(file_path, 'r') as f:
        sample = ''.join([f.readline() for _ in range(num_lines)])
    
    # Check common delimiters
    delimiters = [',', ';', '\t', '|']
    counts = {d: sample.count(d) for d in delimiters}
    
    # Return the delimiter with the highest count
    return max(counts.items(), key=lambda x: x[1])[0]


def import_csv_data(file_path, delimiter=None, header=True, column_mapping=None):
    """
    Import data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        delimiter (str): Delimiter used in the file (auto-detect if None)
        header (bool): Whether the file has a header row
        column_mapping (dict): Mapping of file columns to expected columns
    
    Returns:
        pd.DataFrame: Imported data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Auto-detect delimiter if not provided
    if delimiter is None:
        delimiter = detect_delimiter(file_path)
    
    # Read the CSV file
    df = pd.read_csv(file_path, delimiter=delimiter, header=0 if header else None)
    
    # Apply column mapping if provided
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df


def import_excel_data(file_path, sheet_name=0, column_mapping=None):
    """
    Import data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str or int): Name or index of the sheet to import
        column_mapping (dict): Mapping of file columns to expected columns
    
    Returns:
        pd.DataFrame: Imported data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Apply column mapping if provided
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df


def import_json_data(file_path, record_path=None, column_mapping=None):
    """
    Import data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        record_path (str or list): Path to the records in the JSON
        column_mapping (dict): Mapping of file columns to expected columns
    
    Returns:
        pd.DataFrame: Imported data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    if record_path:
        if isinstance(record_path, str):
            record_path = [record_path]
        
        # Navigate to the specified path in the JSON
        for path in record_path:
            data = data[path]
    
    df = pd.DataFrame(data)
    
    # Apply column mapping if provided
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df


def create_sample_data_files():
    """
    Create sample data files for testing.
    
    Returns:
        tuple: Paths to the created files (sim_data_path, reservation_data_path)
    """
    # Create directory for sample data
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Sample simulation data
    sim_data = [
        ["id_service", "periode", "id_leg", "capacite", "cap_resid", "id_demande", "volume"],
        ["S1", 1, "L1", 100, 80, "D1", 20],
        ["S1", 1, "L2", 100, 70, "D2", 30],
        ["S1", 2, "L1", 100, 90, "D3", 10],
        ["S1", 2, "L2", 100, 85, "D4", 15],
        ["S2", 1, "L3", 150, 120, "D5", 30],
        ["S2", 2, "L3", 150, 100, "D6", 50]
    ]
    
    # Sample reservation data
    reservation_data = [
        ["t_resa", "cat", "orig", "dest", "anticipe", "urgente", "t_avl", "t_due", "vol", "fare", "decision"],
        [1, "A", "O1", "D1", True, False, 5, 10, 20, 100, "accepted"],
        [1, "B", "O1", "D2", False, True, 2, 5, 15, 80, "rejected"],
        [2, "A", "O2", "D1", True, False, 7, 15, 25, 120, "accepted"],
        [2, "B", "O2", "D3", False, False, 10, 20, 30, 150, "accepted"],
        [3, "C", "O3", "D2", True, True, 1, 3, 10, 90, "rejected"]
    ]
    
    # Write to CSV files
    sim_data_path = sample_dir / "simulation_data.csv"
    with open(sim_data_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sim_data)
    
    reservation_data_path = sample_dir / "reservation_data.csv"
    with open(reservation_data_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(reservation_data)
    
    # Write to Excel file (combined)
    excel_path = sample_dir / "logistics_data.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        pd.DataFrame(sim_data[1:], columns=sim_data[0]).to_excel(writer, sheet_name='SimulationData', index=False)
        pd.DataFrame(reservation_data[1:], columns=reservation_data[0]).to_excel(writer, sheet_name='ReservationData', index=False)
    
    # Write to JSON file (combined)
    json_data = {
        "simulation_data": [dict(zip(sim_data[0], row)) for row in sim_data[1:]],
        "reservation_data": [dict(zip(reservation_data[0], row)) for row in reservation_data[1:]]
    }
    
    json_path = sample_dir / "logistics_data.json"
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    return str(sim_data_path), str(reservation_data_path)


if __name__ == "__main__":
    # Create sample data files
    sim_data_path, reservation_data_path = create_sample_data_files()
    
    print(f"Created sample data files:")
    print(f"  - Simulation data: {sim_data_path}")
    print(f"  - Reservation data: {reservation_data_path}")
    
    # Test importing the data
    print("\nImporting CSV data:")
    sim_df = import_csv_data(sim_data_path)
    res_df = import_csv_data(reservation_data_path)
    
    print(f"Imported simulation data: {len(sim_df)} rows")
    print(sim_df.head())
    
    print(f"\nImported reservation data: {len(res_df)} rows")
    print(res_df.head())
