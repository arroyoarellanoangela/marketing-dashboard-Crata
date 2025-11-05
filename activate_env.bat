@echo off
echo Activando entorno virtual para Google Analytics Dashboard...
call venv\Scripts\activate.bat
echo.
echo Entorno virtual activado correctamente!
echo.
echo Para ejecutar la aplicacion, usa:
echo streamlit run app.py
echo.
echo Para desactivar el entorno virtual, usa:
echo deactivate
echo.
cmd /k
