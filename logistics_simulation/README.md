# Logistics Simulation Data Analysis

This project provides tools for analyzing logistics simulation data, focusing on understanding the structure and relationships within simulation parameters and reservation/decision data.

## Features

- Data parsing from CSV files or text input
- Comprehensive data analysis of simulation parameters and reservation decisions
- Visualization of key metrics:
  - Capacity utilization over time
  - Volume distribution by leg
  - Decision distribution
  - Origin-Destination matrix
  - Lead time distribution
- Export of analysis results to JSON format

## Getting Started

### Prerequisites

- Python 3.6+
- Required packages: pandas, numpy, matplotlib, seaborn

### Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install pandas numpy matplotlib seaborn
```

## Usage

### Basic Usage

```python
from simulation_data import LogisticsSimulationAnalyzer

# Initialize the analyzer
analyzer = LogisticsSimulationAnalyzer()

# Load data from files
analyzer.load_data('path/to/simulation_data.csv', 'path/to/reservation_data.csv')

# Or parse data from text
analyzer.parse_data_from_text(sim_data_text, reservation_data_text)

# Analyze the data
results = analyzer.analyze_data()
print(results)

# Create visualizations
analyzer.visualize_data('output_directory')

# Export analysis results
analyzer.export_analysis('analysis_results.json')
```

### Data Format

#### Simulation Data
Expected columns:
- `id_service`: Service identifier
- `periode`: Time period
- `id_leg`: Leg identifier
- `capacite`: Capacity
- `cap_resid`: Residual capacity
- `id_demande`: Demand identifier
- `volume`: Volume

#### Reservation/Decision Data
Expected columns:
- `t_resa`: Reservation time
- `cat`: Category
- `orig`: Origin
- `dest`: Destination
- `anticipe`: Anticipated (boolean)
- `urgente`: Urgent (boolean)
- `t_avl`: Available time
- `t_due`: Due time
- `vol`: Volume
- `fare`: Fare
- `decision`: Decision (accepted/rejected)

## Analysis Metrics

The analyzer provides various metrics including:
- Capacity usage percentage
- Decision distribution
- Origin-destination patterns
- Lead time analysis
- Volume distribution by leg
- Time-based utilization patterns

## Visualization Examples

- Capacity utilization over time (line chart)
- Volume distribution by leg (bar chart)
- Decision distribution (pie chart)
- Origin-Destination matrix (heatmap)
- Lead time distribution (histogram)

## Extending the Analysis

To add custom analysis or visualizations, modify the `analyze_data()` or `visualize_data()` methods in the `LogisticsSimulationAnalyzer` class.
