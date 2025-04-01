#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logistics Simulation Data Analysis

This script processes and analyzes simulation data related to logistics,
focusing on two main tables: simulation parameters and reservations/decisions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import json

# Add a custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class LogisticsSimulationAnalyzer:
    """Class for analyzing logistics simulation data."""
    
    def __init__(self, sim_data_path=None, reservation_data_path=None):
        """
        Initialize the analyzer with paths to data files.
        
        Args:
            sim_data_path (str): Path to simulation data file
            reservation_data_path (str): Path to reservation/decision data file
        """
        self.sim_data_path = sim_data_path
        self.reservation_data_path = reservation_data_path
        self.sim_data = None
        self.reservation_data = None
    
    def load_data(self, sim_data_path=None, reservation_data_path=None):
        """
        Load data from files.
        
        Args:
            sim_data_path (str): Path to simulation data file
            reservation_data_path (str): Path to reservation/decision data file
        
        Returns:
            bool: True if data loaded successfully
        """
        if sim_data_path:
            self.sim_data_path = sim_data_path
        if reservation_data_path:
            self.reservation_data_path = reservation_data_path
            
        try:
            if self.sim_data_path and Path(self.sim_data_path).exists():
                # Assuming CSV format, adjust as needed
                self.sim_data = pd.read_csv(self.sim_data_path)
                print(f"Loaded simulation data with {len(self.sim_data)} rows")
                
            if self.reservation_data_path and Path(self.reservation_data_path).exists():
                # Assuming CSV format, adjust as needed
                self.reservation_data = pd.read_csv(self.reservation_data_path)
                print(f"Loaded reservation data with {len(self.reservation_data)} rows")
                
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def parse_data_from_text(self, sim_data_text=None, reservation_data_text=None):
        """
        Parse data from text strings.
        
        Args:
            sim_data_text (str): Text containing simulation data
            reservation_data_text (str): Text containing reservation data
        
        Returns:
            bool: True if data parsed successfully
        """
        try:
            if sim_data_text:
                # Parse simulation data
                # Expected columns: id_service, periode, id_leg, capacite, cap_resid, id_demande, volume
                lines = [line.strip() for line in sim_data_text.strip().split('\n')]
                data = []
                for line in lines:
                    if line and not line.startswith('#'):  # Skip comments and empty lines
                        values = line.split(',')
                        if len(values) >= 7:  # Ensure we have all expected columns
                            data.append({
                                'id_service': values[0],
                                'periode': int(values[1]),
                                'id_leg': values[2],
                                'capacite': float(values[3]),
                                'cap_resid': float(values[4]),
                                'id_demande': values[5],
                                'volume': float(values[6])
                            })
                
                self.sim_data = pd.DataFrame(data)
                print(f"Parsed simulation data with {len(self.sim_data)} rows")
            
            if reservation_data_text:
                # Parse reservation/decision data
                # Expected columns: t_resa, cat, orig, dest, anticipe, urgente, t_avl, t_due, vol, fare, decision
                lines = [line.strip() for line in reservation_data_text.strip().split('\n')]
                data = []
                for line in lines:
                    if line and not line.startswith('#'):  # Skip comments and empty lines
                        values = line.split(',')
                        if len(values) >= 11:  # Ensure we have all expected columns
                            data.append({
                                't_resa': int(values[0]),
                                'cat': values[1],
                                'orig': values[2],
                                'dest': values[3],
                                'anticipe': values[4].lower() == 'true',
                                'urgente': values[5].lower() == 'true',
                                't_avl': int(values[6]),
                                't_due': int(values[7]),
                                'vol': float(values[8]),
                                'fare': float(values[9]),
                                'decision': values[10]
                            })
                
                self.reservation_data = pd.DataFrame(data)
                print(f"Parsed reservation data with {len(self.reservation_data)} rows")
            
            return True
        except Exception as e:
            print(f"Error parsing data: {e}")
            return False
    
    def analyze_data(self):
        """
        Perform basic analysis on the loaded data.
        
        Returns:
            dict: Analysis results
        """
        results = {}
        
        if self.sim_data is not None:
            # Simulation data analysis
            results['sim_data'] = {
                'row_count': len(self.sim_data),
                'summary': self.sim_data.describe().to_dict(),
                'capacity_usage': (1 - self.sim_data['cap_resid'].sum() / self.sim_data['capacite'].sum()) * 100,
                'unique_services': self.sim_data['id_service'].nunique(),
                'unique_legs': self.sim_data['id_leg'].nunique(),
                'periods': {
                    'min': self.sim_data['periode'].min(),
                    'max': self.sim_data['periode'].max(),
                    'count': self.sim_data['periode'].nunique()
                }
            }
        
        if self.reservation_data is not None:
            # Reservation data analysis
            results['reservation_data'] = {
                'row_count': len(self.reservation_data),
                'summary': self.reservation_data.describe().to_dict(),
                'decision_counts': self.reservation_data['decision'].value_counts().to_dict(),
                'origin_counts': self.reservation_data['orig'].value_counts().to_dict(),
                'destination_counts': self.reservation_data['dest'].value_counts().to_dict(),
                'category_counts': self.reservation_data['cat'].value_counts().to_dict(),
                'anticipation_ratio': self.reservation_data['anticipe'].mean() * 100,
                'urgency_ratio': self.reservation_data['urgente'].mean() * 100
            }
            
            # Calculate average lead time (t_due - t_avl)
            if 't_due' in self.reservation_data.columns and 't_avl' in self.reservation_data.columns:
                self.reservation_data['lead_time'] = self.reservation_data['t_due'] - self.reservation_data['t_avl']
                results['reservation_data']['avg_lead_time'] = self.reservation_data['lead_time'].mean()
        
        return results
    
    def visualize_data(self, output_dir=None):
        """
        Create visualizations of the data.
        
        Args:
            output_dir (str): Directory to save visualizations
        
        Returns:
            list: Paths to saved visualization files
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        # Set style
        sns.set(style="whitegrid")
        
        if self.sim_data is not None:
            # 1. Capacity utilization over periods
            plt.figure(figsize=(12, 6))
            period_data = self.sim_data.groupby('periode').agg({
                'capacite': 'sum',
                'cap_resid': 'sum'
            }).reset_index()
            period_data['utilization'] = 1 - (period_data['cap_resid'] / period_data['capacite'])
            
            plt.plot(period_data['periode'], period_data['utilization'] * 100, marker='o')
            plt.title('Capacity Utilization Over Time')
            plt.xlabel('Period')
            plt.ylabel('Utilization (%)')
            plt.grid(True)
            
            if output_dir:
                file_path = os.path.join(output_dir, 'capacity_utilization.png')
                plt.savefig(file_path)
                saved_files.append(file_path)
                plt.close()
            else:
                plt.show()
            
            # 2. Volume distribution by leg
            plt.figure(figsize=(12, 6))
            leg_volume = self.sim_data.groupby('id_leg')['volume'].sum().sort_values(ascending=False)
            leg_volume.plot(kind='bar')
            plt.title('Total Volume by Leg')
            plt.xlabel('Leg ID')
            plt.ylabel('Total Volume')
            plt.xticks(rotation=45)
            
            if output_dir:
                file_path = os.path.join(output_dir, 'volume_by_leg.png')
                plt.savefig(file_path)
                saved_files.append(file_path)
                plt.close()
            else:
                plt.show()
        
        if self.reservation_data is not None:
            # 3. Decision distribution
            plt.figure(figsize=(10, 6))
            self.reservation_data['decision'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Distribution of Decisions')
            plt.ylabel('')
            
            if output_dir:
                file_path = os.path.join(output_dir, 'decision_distribution.png')
                plt.savefig(file_path)
                saved_files.append(file_path)
                plt.close()
            else:
                plt.show()
            
            # 4. Origin-Destination heatmap
            plt.figure(figsize=(12, 10))
            od_matrix = pd.crosstab(self.reservation_data['orig'], self.reservation_data['dest'])
            sns.heatmap(od_matrix, annot=True, cmap='YlGnBu', fmt='d')
            plt.title('Origin-Destination Matrix')
            plt.xlabel('Destination')
            plt.ylabel('Origin')
            
            if output_dir:
                file_path = os.path.join(output_dir, 'od_matrix.png')
                plt.savefig(file_path)
                saved_files.append(file_path)
                plt.close()
            else:
                plt.show()
            
            # 5. Lead time distribution
            if 'lead_time' in self.reservation_data.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(self.reservation_data['lead_time'], kde=True)
                plt.title('Distribution of Lead Times')
                plt.xlabel('Lead Time (t_due - t_avl)')
                plt.ylabel('Count')
                
                if output_dir:
                    file_path = os.path.join(output_dir, 'lead_time_distribution.png')
                    plt.savefig(file_path)
                    saved_files.append(file_path)
                    plt.close()
                else:
                    plt.show()
        
        return saved_files
    
    def export_analysis(self, output_file):
        """
        Export analysis results to a JSON file.
        
        Args:
            output_file (str): Path to output file
        
        Returns:
            bool: True if export successful
        """
        try:
            analysis_results = self.analyze_data()
            
            with open(output_file, 'w') as f:
                json.dump(analysis_results, f, indent=2, cls=NumpyEncoder)
            
            print(f"Analysis exported to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting analysis: {e}")
            return False


def main():
    """Main function to demonstrate the analyzer's capabilities."""
    # Example usage
    analyzer = LogisticsSimulationAnalyzer()
    
    # Example simulation data (replace with actual data)
    sim_data_example = """
    # id_service, periode, id_leg, capacite, cap_resid, id_demande, volume
    S1,1,L1,100,80,D1,20
    S1,1,L2,100,70,D2,30
    S1,2,L1,100,90,D3,10
    S1,2,L2,100,85,D4,15
    S2,1,L3,150,120,D5,30
    S2,2,L3,150,100,D6,50
    """
    
    # Example reservation data (replace with actual data)
    reservation_data_example = """
    # t_resa, cat, orig, dest, anticipe, urgente, t_avl, t_due, vol, fare, decision
    1,A,O1,D1,true,false,5,10,20,100,accepted
    1,B,O1,D2,false,true,2,5,15,80,rejected
    2,A,O2,D1,true,false,7,15,25,120,accepted
    2,B,O2,D3,false,false,10,20,30,150,accepted
    3,C,O3,D2,true,true,1,3,10,90,rejected
    """
    
    # Parse example data
    analyzer.parse_data_from_text(sim_data_example, reservation_data_example)
    
    # Analyze data
    analysis_results = analyzer.analyze_data()
    print("Analysis Results:")
    print(json.dumps(analysis_results, indent=2, cls=NumpyEncoder))
    
    # Create visualizations
    output_dir = "visualizations"
    saved_files = analyzer.visualize_data(output_dir)
    print(f"Saved {len(saved_files)} visualization files to {output_dir}")
    
    # Export analysis
    analyzer.export_analysis("analysis_results.json")


if __name__ == "__main__":
    main()
