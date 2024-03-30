# ShortLink-py

This project is a URL shortener implemented in Python using the FastAPI framework.

## Getting Started

### Prerequisites

 - Docker
 - Python 3.8+
 - pip

## Running the Application

### Using Docker

1. Install Docker and Docker Compose on your machine.

2. Clone the repository and navigate to the project root directory.

3. Run the application using:

   ```
   docker-compose up
   ```

4. The application should now be running and accessible at `http://localhost:8080`.

### Using Makefile

1. Install and run Postgres

2. Install and run Redis

3. Clone the repository and navigate to the project root directory.

4. Configure the connection using environment variables ([see .env.example](.env.example))

5. Run the application using:

   ```
   make run
   ```

6. The application should now be running and accessible at `http://localhost:8080`.

## Testing the Application

   ```
   make test
   ```

To generate a test coverage report:

   ```
   make test-coverage
   ```

## License

This project is licensed under the [MIT License](LICENSE).
