Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " INICIALIZACION DE BASE DE DATOS DIQUIS" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Intentar encontrar psql.exe en los directorios de instalacion comunes de Windows
$psqlPath = ""
$postgresPaths = @(
    "C:\Program Files\PostgreSQL\*\bin\psql.exe",
    "C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe"
)

foreach ($path in $postgresPaths) {
    $found = Resolve-Path $path -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($found) {
        $psqlPath = $found.Path
        break
    }
}

if (-not $psqlPath) {
    # Probar si esta en el PATH global
    if (Get-Command psql -ErrorAction SilentlyContinue) {
        $psqlPath = "psql"
    } else {
        Write-Host "[!] Error: No se encontro psql.exe en tu sistema Windows." -ForegroundColor Red
        Write-Host "Asegurate de tener PostgreSQL instalado en C:\Program Files\PostgreSQL\" -ForegroundColor Yellow
        exit
    }
}

Write-Host "[+] PostgreSQL detectado nativamente en Windows: $psqlPath" -ForegroundColor Green

$dbUser = "postgres"
$dbName = "diquis"
$sqlFile = ".\ddl\0. Init Completo.sql"

# Paso 1: Crear la base de datos (Ignorar error rojo si ya existe)
Write-Host ""
Write-Host "[*] Paso 1: Creando la base de datos '$dbName' (si no existe)..." -ForegroundColor Yellow
& $psqlPath -U $dbUser -d postgres -c "CREATE DATABASE $dbName;" 2>$null

# Paso 2: Ejecutar el script SQL maestro
Write-Host ""
Write-Host "[*] Paso 2: Ejecutando script maestro en '$dbName'..." -ForegroundColor Yellow
Write-Host "Se solicitara tu contrasena de PostgreSQL para continuar." -ForegroundColor DarkGray

& $psqlPath -U $dbUser -d $dbName -f $sqlFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[+] Base de datos inicializada con exito! Todas las tablas, triggers y datos estan listos." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[!] Ocurrio un error al ejecutar el script SQL. Revisa los mensajes en consola." -ForegroundColor Red
}
