# Production Plan API

## Requirements

- Python 3.7
- pip

## Instalation

1. Clone repository
2. Create virtual enviroment:
   python -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Execute application
   uvicorn main:app --host 0.0.0.0 --port 8888 --reload
   The API will be available in http://localhost:8888
