@echo off
setlocal
cd /d %~dp0\..

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
  copy .env.example .env
)

python init_db.py
python seed_data.py

echo.
echo Proyecto listo.
echo Ejecuta:
echo   .venv\Scripts\activate
echo   python run.py
endlocal
