# Final Year Project Documentation

## 1. Project Title
AI-Enabled Smart Waste Segregation and Collection Route Optimization System

## 2. Abstract
Rapid urbanization has led to significant challenges in municipal waste management. Inefficient waste segregation at the source and unoptimized collection routes result in increased operational costs and environmental degradation. This project proposes a comprehensive web-based system to address these issues. By leveraging image feature extraction for waste classification, the system can automatically segregate waste into predefined categories (e.g., Organic, Recyclable Plastic, General Trash). Furthermore, the system incorporates a route optimization engine using the Nearest Neighbor algorithm and Haversine distance to calculate the most efficient path for waste collection vehicles, taking into account bin fill levels, priorities, and vehicle capacity constraints. The solution provides a centralized dashboard for real-time monitoring and an admin portal for system management, offering a practical, low-cost approach to smart city waste management.

## 3. Introduction
Waste management is a critical service provided by municipal authorities. However, traditional methods rely heavily on manual sorting and static collection schedules. Often, collection vehicles visit bins that are only partially full, wasting fuel and time, while overflowing bins are ignored. Additionally, improper segregation at the source contaminates recyclable materials. This project introduces a smart, automated approach by combining web technologies, basic artificial intelligence/statistical classification for waste segregation, and geospatial algorithms for dynamic route planning, ensuring a more sustainable and efficient waste management ecosystem.

## 4. Problem Statement
The current municipal solid waste management system suffers from two major inefficiencies:
1. **Lack of Automated Segregation:** Waste is often dumped mixed, and manual segregation is slow, hazardous, and expensive.
2. **Static Routing:** Garbage collection trucks follow fixed daily routes regardless of the actual fill level of the bins, leading to unnecessary fuel consumption, higher carbon emissions, and uncollected overflowing bins.

## 5. Objectives
- To develop a user-friendly web interface for waste reporting and tracking.
- To implement an automated image-based classification module to categorize waste types.
- To dynamically calculate the shortest and most efficient collection routes for waste trucks based on current bin fill levels.
- To design a centralized dashboard and admin portal to monitor system statistics, users, and historical data.

## 6. Existing System
In the existing system, waste is collected based on predefined, static schedules without real-time data on bin capacity. Segregation is entirely reliant on citizens manually separating waste into color-coded bins, which is prone to human error. There is no centralized digital platform for authorities to monitor the daily waste collection process, leading to a lack of transparency and data-driven decision-making.

## 7. Proposed System
The proposed system is a centralized web application where:
- Users can upload images of waste to automatically identify its category and receive disposal suggestions.
- The system maintains a digital map of all collection bins, tracking their fill levels, weights, and priority status.
- A route optimization algorithm dynamically computes the best path for collection vehicles, prioritizing urgent bins and factoring in truck payload capacity.
- Administrators have access to a secure dashboard to view overall system analytics, user registrations, and waste history.

## 8. Methodology
The project was developed using an Agile methodology, broken down into distinct, verifiable modules:
1. **Requirement Analysis & Design:** Defining database schemas and UI/UX design components (using modern dark-mode aesthetics).
2. **Backend Development:** Building modular blueprints for Authentication, Classification, Routes, Dashboard, and Admin using the Flask framework.
3. **Algorithm Integration:** Implementing the statistical image analysis function for segregation and the Nearest Neighbor algorithm for routing.
4. **Integration & Testing:** Unifying all blueprints and running unit/integration testing to ensure seamless database communication and error handling.

## 9. System Architecture
The project follows a standard Client-Server Architecture:
- **Client Side (Frontend):** Developed using HTML5, CSS3, and Vanilla JavaScript. It uses **Chart.js** for rendering interactive dashboard analytics and **Leaflet.js** for rendering geographic maps and routes.
- **Server Side (Backend):** Developed using Python and the **Flask** web framework, structured using Flask Blueprints for modularity.
- **Database:** Uses **SQLite** via **Flask-SQLAlchemy** ORM for local data persistence, handling Users, Waste History, Collection Points, and Routes.

## 10. Modules
The system is divided into five core modules:
1. **Authentication Module:** Handles secure user registration, login, and session management. Distinguishes between standard users and administrators.
2. **AI Waste Segregation Module:** Accepts an image upload, analyzes it, and outputs the waste category, type, confidence score, and bin color recommendation.
3. **Route Optimization Module:** Manages the geolocation of waste bins and calculates the most efficient vehicle routing paths.
4. **Dashboard Module:** A user-facing analytics page displaying metrics like total waste records, category distribution charts, and recent activity.
5. **Admin Module:** A secure portal for administrators to view and manage registered users, system-wide waste detections, and optimal route history.

## 11. Technologies Used
- **Programming Language:** Python 3.x
- **Web Framework:** Flask
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** HTML5, CSS3 (Custom Variables, Glassmorphism), JavaScript
- **Libraries:** Werkzeug (Security), Chart.js (Data Visualization), Leaflet.js (Mapping)
- **Testing:** Python `unittest`

## 12. AI/ML Algorithm
The waste classification is handled by a deterministic image feature extraction engine. Rather than requiring high compute power for deep Convolutional Neural Networks, the implemented script (`predict.py`) extracts statistical features directly from the raw image byte sequence. It calculates the average byte value from a sample size to map the image to one of six predefined categories:
1. Organic (Wet)
2. Recyclable Plastic
3. Dry Paper & Cardboard
4. Recyclable Glass
5. Recyclable Metal
6. Non-Recyclable Trash

This lightweight approach ensures immediate processing times suitable for a real-time web application demonstration.

## 13. Waste Segregation Process
1. The user navigates to the "Classify Waste" page and uploads an image.
2. The image is passed to the backend `WasteClassifier`.
3. The image bytes are analyzed to generate a feature score.
4. The score is mapped to a specific waste category and generates a confidence percentage.
5. The result (including disposal suggestion and recommended bin color) is displayed to the user and securely logged in the `WasteHistory` database table.

## 14. Route Optimization Process
The system optimizes collection routes using the **Nearest Neighbor Heuristic** combined with the **Haversine Distance Formula**:
1. **Filtering:** The system first identifies "urgent" bins (fill level >= 50% or priority >= 4).
2. **Distance Calculation:** The Haversine formula calculates the Great-Circle distance between geographic coordinates (Latitude, Longitude) accounting for the Earth's curvature.
3. **Routing:** Starting from the central depot, the algorithm iteratively selects the nearest unvisited bin.
4. **Capacity Constraints:** If the accumulated weight of collected waste exceeds the vehicle's capacity (e.g., 1000 kg), the truck is routed back to the depot to unload before continuing.
5. **Output:** The final route is returned with estimated travel time (based on average urban speed), total distance, and fuel consumption, then plotted visually on a Leaflet map.

## 15. Database Design
The SQLite database contains the following relational tables:
- **User:** Stores `id`, `username`, `email`, `password_hash`, `role`, `created_at`.
- **WasteHistory:** Stores `id`, `user_id`, `category`, `confidence`, `image_ref`, `timestamp`.
- **CollectionPoint:** Stores `id`, `location_name`, `latitude`, `longitude`, `current_fill_level`, `current_weight_kg`, `priority`.
- **RouteHistory:** Stores `id`, `generated_by`, `total_distance_km`, `estimated_time_mins`, `fuel_used_liters`, `timestamp`.

## 16. Results
The finalized system successfully integrates all proposed modules. Users can seamlessly register, log in, and upload waste images to receive immediate classification feedback. The route optimization engine correctly calculates distances, respects vehicle capacity, and plots interactive maps. The admin dashboard successfully aggregates database records into readable charts, and all integration tests pass flawlessly.

## 17. Advantages
- **Operational Efficiency:** Reduces fuel consumption and time by preventing trucks from visiting empty bins.
- **Cost-Effective:** Lightweight implementation reduces server overhead.
- **User-Friendly:** The modern, responsive UI encourages public participation in waste sorting.
- **Data-Driven:** The dashboard provides authorities with actionable insights into waste generation patterns.

## 18. Limitations
- **No Real-Time Traffic Data:** The route optimizer assumes a constant average speed and straight-line Haversine distance, lacking integration with real-world road network constraints or live traffic APIs.
- **Scalability:** The local SQLite database is excellent for demonstration but must be migrated to a dedicated database server (like PostgreSQL) for a large-scale municipal deployment.
- **Classification Approach:** The current statistical byte-feature classifier is a proof-of-concept; a production environment would require a trained Deep Learning CNN model on a massive dataset of local waste for high-accuracy visual recognition.

## 19. Future Scope
- **IoT Integration:** Integrating physical smart bins equipped with ultrasonic sensors to send real-time fill levels to the database automatically.
- **Advanced AI Models:** Upgrading the backend classifier to a TensorFlow/PyTorch-based computer vision model (e.g., YOLO or ResNet) for complex object detection in cluttered bins.
- **Mobile Application:** Porting the web application to a cross-platform mobile app (React Native/Flutter) for on-the-go reporting by citizens and drivers.

## 20. Conclusion
The "AI-Enabled Smart Waste Segregation and Collection Route Optimization System" demonstrates how software engineering, basic data classification, and optimization algorithms can modernize traditional municipal services. By providing a centralized platform for both citizens and administrators, the project successfully lays the groundwork for a scalable smart city waste management infrastructure, achieving all defined academic objectives.
