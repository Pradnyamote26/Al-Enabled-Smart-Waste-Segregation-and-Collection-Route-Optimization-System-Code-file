# AI-Enabled Smart Waste Segregation and Collection Route Optimization System

An intelligent, data-driven software solution combining Deep Learning-based waste classification with Vehicle Routing Problem (VRP) route optimization for smart municipal waste management.

## Project Architecture

- **`backend/`**: Flask REST API server and service handlers
- **`templates/` / `static/`**: Web dashboard interface (HTML5 / CSS3 / Vanilla JS)
- **`ml_model/`**: Deep Learning model scripts (CNN / ResNet50) for waste classification
- **`route_optimization/`**: Path planning engine for minimizing travel distance, fuel, and time
- **`database/`**: Database models (SQLAlchemy) and initialization scripts
- **`dataset/`**: Waste image dataset placeholders and pre-processing pipeline
- **`config/`**: System configuration and environment settings
- **`docs/`**: Project documentation and architecture specs

## Quick Start Guide

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database:**
   ```bash
   python -m database.db_init
   ```

3. **Run the Backend Application:**
   ```bash
   python -m backend.app
   ```

4. Access the web dashboard at `http://127.0.0.1:5000`.
