# Music Streaming Service Data Generator

## Overview

This project is part of a thesis work that focuses on simulating a music streaming service to analyze user behavior and
the popularity of different music genres and artists.
It uses Python to generate synthetic data, and then apply the generated data on collaborative filtering recommendation
system and prediction system.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Supervico0097/Synthetic-Data-Generator.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd Synthetic-Data-Generator
   ```
3. **Install dependencies:**
   ```bash
   1) poetry install
   2) poetry shell
   ```

## Usage

Run the simulation and evaluation scripts as follows:

- **Set Configuration Parameters**
  Open and configure in config_music.yaml

- **Generate synthetic data:**
  ```bash
  python data_generator.py
  ```
- **Collaborative filtering (Recommender):**
   1) Open colaborative_filtering.py and adjust the "num_recommendation", "num_neighbors", "num_users"
   2) Run the colaborative filtering
      
      ```bash
      python colaborative_filtering.py
       ```

- **Predictor:**
  1) Open Jupyter
     
     ```bash
     jupyter notebook
     ```
    2) Open "notebooks"
    3) Run "Generate_Training_Data.ipynb"
    4) Open "ml.ipnyb" and configure "weeks" parameter
    5) run "ml.ipnyb"

## Directory Structure

- `data/`: Contains generated datasets.
- `tests/`: Contains unit tests for the modules.
- `notebooks/`: Jupyter notebooks for the predictor
- `*.py`: Python scripts for different components of the simulation.

## Contributing

Contributions to the project are welcome.

