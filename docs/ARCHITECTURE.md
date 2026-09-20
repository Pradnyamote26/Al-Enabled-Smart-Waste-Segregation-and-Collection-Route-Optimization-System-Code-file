# System Architecture & Technical Specifications

## 1. Deep Learning Image Classification Subsystem
- **Model:** ResNet50 Transfer Learning / Convolutional Neural Network (CNN)
- **Input:** RGB waste image (224x224x3)
- **Output:** Categorical probability across 6 waste classes: Organic (wet), Paper, Cardboard, Plastic, Glass, Metal.
- **Framework:** TensorFlow / Keras, OpenCV

## 2. Route Optimization Subsystem
- **Problem Formulation:** Capacitated Vehicle Routing Problem (CVRP)
- **Algorithm:** Nearest-Neighbor Heuristic / Dijkstra's Shortest Path with capacity & priority constraints.
- **Metrics Evaluated:** Haversine spatial distance (km), estimated time (mins), fuel consumption (L).

## 3. Web & Application Layer
- **Backend:** Python Flask REST APIs
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Leaflet.js / Google Maps API
- **Database:** SQLite / PostgreSQL (SQLAlchemy ORM)
