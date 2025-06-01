@echo off
echo Stopping and removing existing containers...
docker-compose down -v

echo Building and starting containers with fresh database...
docker-compose up --build -d

echo Waiting for services to start...
timeout /t 10 /nobreak > nul

echo Checking container status...
docker-compose ps

echo.
echo Setup complete! Admin user is ready:
echo Username: admin
echo Password: admin123
echo.
echo Access the application at: http://localhost
echo API available at: http://localhost:5000
echo.
echo To view logs, run: docker-compose logs -f
