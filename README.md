Setup

1. Clone the repository
2. Create a virtual environment
3. Install Python dependencies

pip install -r backend/requirements.txt

4. Install Angular dependencies

cd frontend
npm install

5. Create the environment file

Copy backend/.env.example to backend/.env

6. Fill in your database and API keys.

7. Run Alembic migrations

alembic upgrade head

8. Start FastAPI

uvicorn app.main:app --reload

9. Start Angular

cd frontend
ng serve
