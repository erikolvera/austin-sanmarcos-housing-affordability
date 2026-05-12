# Austin-San Marcos Housing Affordability Analysis

A data-driven analysis and interactive dashboard exploring housing affordability, pricing pressures, and spatial inequality in the Austin to San Marcos corridor.

## Overview

This project investigates the divergence between home prices and local wages, the spillover demand affecting the I-35 corridor, and the geographic distribution of affordable housing. The analysis is presented through an **Interactive Dashboard**: A Streamlit application for exploring the data interactively.

## Data Sources

The analysis relies on four primary datasets:
- **Zillow Home Value Index (ZHVI)**: Typical home values over time for Austin and San Marcos.
- **Zillow Income-Needed Metric**: The required household income to afford a median-priced home in the Austin Metro.
- **Redfin Data Center**: Weekly active inventory and median sale prices.
- **City of Austin Open Data**: Geographic coordinates and unit counts for affordable housing properties.

## Getting Started

### Prerequisites
Make sure you have Python installed. It is recommended to use a virtual environment.

### Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Dashboard

To launch the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

