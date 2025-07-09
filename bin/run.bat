@echo off
setlocal enabledelayedexpansion
REM Build and Run ENEM Spark Pipeline
REM This script builds the Docker image and runs the complete pipeline

echo ENEM Big Data Pipeline
echo =========================
echo.
echo Escolha o tipo de dados para processar:
echo 1^) Dados locais ^(rapido, apenas amostra de 15 registros^)
echo 2^) Dados reais do ENEM ^(completo, ~13M registros, demora varias horas^)
echo.
set /p choice="Digite sua escolha (1 ou 2): "

if "%choice%"=="1" (
    echo.
    echo ✅ Usando dados locais ^(amostra pequena^)
    echo 📊 Processando 15 registros de exemplo...
    set USE_LOCAL_DATA=true
) else if "%choice%"=="2" (
    echo.
    echo ⚠️  Usando dados reais do ENEM
    echo 📊 Processando ~13 milhoes de registros...
    echo ⏰ Tempo estimado: 6-8 horas
    echo.
    set /p confirm="Tem certeza? (y/N): "
    if /i "!confirm!"=="y" (
        set USE_LOCAL_DATA=false
    ) else (
        echo Operacao cancelada.
        exit /b 0
    )
) else (
    echo Escolha invalida. Use 1 ou 2.
    exit /b 1
)

echo.
echo Building Docker image...
docker build -t enem-spark-job -f misc/Dockerfile .

echo.
echo Starting services with Docker Compose...
cd misc
docker-compose up --scale spark-worker=2 --scale datanode=1 -d

echo.
echo Pipeline started successfully!
echo Access Spark Master UI at: http://localhost:8080
echo Access HDFS UI at: http://localhost:9870
echo.
if "%USE_LOCAL_DATA%"=="true" (
    echo 📈 Processando dados locais ^(rapido^)...
) else (
    echo 📈 Processando dados reais ^(pode demorar varias horas^)...
)
echo.
echo To stop the services, run: bin\stop.bat
