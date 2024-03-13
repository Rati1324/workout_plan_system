# Workout Plan System in FastAPI

This repository contains a FastAPI project for a workout planning system that can be easily set up and run using Docker Compose.
It uses PostgreSQL as the datbase and Redis for caching when using websockets.

## Prerequisites

Make sure you have the following software installed on your system:

- Docker: [Installation Guide](https://docs.docker.com/get-docker/)
- Docker Compose: [Installation Guide](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Rati1324/workout_plan_system.git
   ```
2. Build and start the Docker containers:

   ```bash
   docker-compose up --build
   ```
   This command will build the Docker images and start the containers defined in docker-compose.yml.

3. Access the FastAPI application in your browser:
    API documentation (Swagger): http://localhost:8000/docs

    Interactive ReDoc documentation: http://localhost:8000/redoc

    Real-time workout session tracker documentation: http://localhost:8000/websocket_docs 

You can now interact with and test your FastAPI application using the provided documentation.

To stop the application and remove the Docker containers, press Ctrl+C in the terminal where docker-compose up is running, and then run:
   
   ```bash
   docker-compose down
   
