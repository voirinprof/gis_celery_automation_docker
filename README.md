# Geomatics: Spatial Buffer Analysis with Celery, RabbitMQ, and Docker Compose

This project illustrates a simple geomatics application that calculates buffers around geographic points. It uses **Flask** for the web interface, **Celery** for asynchronous task processing, **RabbitMQ** as the message broker, **Redis** as the result backend, **GeoPandas** and **Shapely** for geospatial calculations, and **SQLite** for data storage. The orchestration is managed by **Docker Compose**, and the results are displayed on a **Leaflet** map.

## Prerequisites
- Docker
- Docker Compose

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/voirinprof/gis_celery_automation_docker.git
   cd gis_celery_automation_docker
   ```
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:5000`.

## Usage
- Click on the map to add points, specifying a buffer radius (in meters) via the "Buffer Radius" field.
- Click "Calculate Buffers" to launch an asynchronous computation task via Celery.
- The task status is displayed in real-time, and the buffers are shown on the map as translucent blue polygons once the computation is complete.

## Structure
- `app/` : Contains the Flask application, Celery tasks, HTML templates, and static files (CSS, JS).
- `docker-compose.yml` : Orchestrates the services (web, rabbitmq, redis, celery).

## Celery and Approach
### Overview of Celery
**Celery** is a distributed task queue system that enables asynchronous execution of geomatics tasks, such as spatial buffer calculations. In this project, Celery uses **RabbitMQ** as the message broker to manage the task queue and **Redis** as the backend to store task results.

### Approach for Asynchronous Computation
1. **Problem Definition** :
   - **Points** : Each point has a latitude, longitude, and buffer radius (in meters).
   - **Objective** : Calculate buffer polygons around each point for spatial analysis.
2. **Data Preparation** :
   - **Storage** : Points and their radii are stored in an SQLite database.
   - **Geometry** : GeoPandas and Shapely create geometric objects (points and buffers).
3. **Celery Configuration** :
   - A Celery task (`compute_buffers_task`) calculates buffers using GeoPandas.
   - RabbitMQ manages the task queue, and Redis stores results as GeoJSON.
   - Celery workers process the task in the background, freeing up the Flask application.
4. **Execution and Results** :
   - The user triggers a task via the web interface.
   - Flask sends the task to Celery and returns a task ID.
   - The frontend polls the task status and displays the buffers once complete.

### Why Use RabbitMQ and Redis Together?
In this application, **RabbitMQ** and **Redis** play complementary roles in Celery's architecture, ensuring efficient and reliable handling of asynchronous tasks.

#### Role of RabbitMQ (Message Broker)
- **Queue Management** : RabbitMQ, based on the AMQP protocol, receives tasks (e.g., `compute_buffers_task`) sent by Flask and places them in a queue for distribution to Celery workers. This ensures the application remains responsive, even for computationally intensive geospatial tasks.
- **Reliability** : RabbitMQ persists tasks to disk, preventing loss in case of worker or broker failure. This is critical for geomatics tasks where losing a task could disrupt analysis.
- **Scalability** : RabbitMQ supports complex queues and can distribute tasks to multiple workers, useful if the application needs to process many points.
- **Monitoring** : RabbitMQ's management interface (accessible at `http://localhost:15672`) allows monitoring of queues and debugging issues.

#### Role of Redis (Result Backend)
- **Result Storage** : Redis, a fast in-memory database, stores task results (e.g., GeoJSON of calculated buffers). This enables the frontend to quickly retrieve results via the `/task_status/<task_id>` API for display on the Leaflet map.
- **Performance** : Redis's in-memory operations ensure low latency, critical for frequent polling in the `map.js` script.
- **Simplicity** : Redis uses a simple key-value structure to store JSON-serialized results, aligning with Celery's configuration (`result_serializer = 'json'`).
- **Data Expiration** : Redis can automatically delete results after a set time, reducing memory usage.

#### Why Both?
- **Separation of Responsibilities** : RabbitMQ excels at robust queue management, while Redis is optimized for fast result storage. This separation enhances reliability and performance.
- **Optimization** : RabbitMQ ensures task persistence and distribution, while Redis provides quick result retrieval, essential for a responsive user interface.
- **Standard Practice** : The RabbitMQ (broker) and Redis (backend) combination is recommended by Celery's documentation for balancing reliability and efficiency, especially in geomatics applications with intensive computations.
- **Workflow** : When a user clicks "Calculate Buffers," Flask sends the task to RabbitMQ, which distributes it to a worker. The worker computes the buffers and stores the GeoJSON in Redis. The frontend retrieves this result from Redis for map display.

#### Alternatives
While Redis can technically serve as a broker, it lacks features like message persistence, making RabbitMQ more suitable for a reliable broker. Using RabbitMQ as a backend is possible but less efficient than Redis for fast result storage.

### Best Practices
- **Verify Connections** : Ensure RabbitMQ and Redis are accessible (use `rabbitmq` and `redis` as hostnames in Docker).
- **Monitor Tasks** : Add Flower for monitoring (e.g., extend `docker-compose.yml` to include `celery flower`).
- **Optimize Data** : Limit the number of points for optimal performance.
- **Handle Errors** : Configure retries in `celery_config.py` to manage failures.

## Geomatics Context
This project leverages geomatics tools to:
- **Manage Points** : Store geographic coordinates and attributes (radius) in SQLite.
- **Calculate Buffers** : GeoPandas and Shapely generate buffer polygons, accounting for cartographic projections (e.g., UTM for accurate measurements).
- **Visualize** : Leaflet displays buffers as GeoJSON on an interactive map.

## Resources
- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/)
- [GeoPandas Documentation](https://geopandas.org/)
- [Celery with Flask Tutorial](https://flask.palletsprojects.com/en/2.3.x/patterns/celery/)