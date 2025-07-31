@echo off
echo ========================================
echo    East West App - Build Script
echo ========================================

REM Limpiar builds anteriores
echo Limpiando archivos anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Creando ejecutable...
echo Esto puede tomar varios minutos...

REM Crear ejecutable
pyinstaller main.spec --clean --noconfirm

REM Verificar resultado
if exist "dist\EastWestApp.exe" (
    echo.
    echo ========================================
    echo   BUILD EXITOSO!
    echo ========================================
    echo Ejecutable creado en: dist\EastWestApp.exe
    
    REM Mostrar tamaño del archivo
    for %%I in ("dist\EastWestApp.exe") do (
        set size=%%~zI
        set /a sizeInMB=!size!/1024/1024
        echo Tamaño: !sizeInMB! MB
    )
    
    echo.
    echo Para probar: cd dist ^&^& EastWestApp.exe
) else (
    echo.
    echo ========================================
    echo   BUILD FALLO!
    echo ========================================
    echo Revisa los errores arriba
)

echo.
pause