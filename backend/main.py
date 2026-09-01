from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt
import uuid
import models
from database import engine, get_db
import requests

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Słownik w pamięci RAM serwera przechowujący aktywne tickety: { "ticket_uuid": "nazwa_użytkownika" }
SESSION_TICKETS = {}

@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    if not username.strip() or not password.strip():
        raise HTTPException(status_code=400, detail="Login i hasło nie mogą być puste!")

    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    new_user = models.User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Konto założone!"}

@app.post("/login")
def login_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Nieprawidłowy login lub hasło")
        
    is_password_correct = bcrypt.checkpw(password.encode('utf-8'), db_user.hashed_password.encode('utf-8'))
    
    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Nieprawidłowy login lub hasło")
    
    # Generujemy bezpieczny, jednorazowy ticket sesji dla gracza
    ticket = str(uuid.uuid4())
    SESSION_TICKETS[ticket] = db_user.username
    
    return {
        "message": "Zalogowano pomyślnie!", 
        "user": db_user.username,
        "ticket": ticket,
        "status": "active_session"
    }

@app.post("/add-achievement")
def add_achievement(data: dict, db: Session = Depends(get_db)):
    ticket = data.get("ticket")
    achievement_name = data.get("achievement")
    action_time = data.get("action_time", 15.0)
    
    # Weryfikacja ticketu w pamięci RAM
    if not ticket or ticket not in SESSION_TICKETS:
        raise HTTPException(status_code=401, detail="Nieprawidłowy lub wygasły ticket sesji!")
        
    # Pobieramy login powiązany z ticketem
    username = SESSION_TICKETS[ticket]
    
    # Opcjonalnie: usuwamy ticket po użyciu, jeśli ma być strictly jednorazowy:
    # del SESSION_TICKETS[ticket]

    # 1. Przekazanie danych do mikroserwisu Clojure
    calculated_score = 0.0
    speedrun_status = False
    
    try:
        clojure_payload = {"actions": [float(action_time)]}
        clojure_res = requests.post("http://localhost:8080", json=clojure_payload, timeout=2)
        
        if clojure_res.status_code == 200:
            clojure_data = clojure_res.json()
            calculated_score = clojure_data.get("total-score", 0.0)
            speedrun_status = clojure_data.get("speedrun-achieved", False)
    except Exception as e:
        print("Błąd połączenia z Clojure:", e)

    # 2. Weryfikacja użytkownika w bazie
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")
        
    # 3. Zapis/Aktualizacja osiągnięcia w PostgreSQL
    existing_ach = db.query(models.Achievement).filter(
        models.Achievement.user_id == user.id,
        models.Achievement.name == achievement_name
    ).first()
    
    if existing_ach:
        existing_ach.total_score = calculated_score
        existing_ach.is_speedrun = speedrun_status
        db.commit()
        return {
            "status": "success", 
            "message": f"Zaktualizowano wynik dla: {achievement_name}",
            "saved_score": calculated_score,
            "is_speedrun": speedrun_status
        }
        
    new_ach = models.Achievement(
        name=achievement_name, 
        description="Zdobyto w grze VR", 
        user_id=user.id,
        total_score=calculated_score,
        is_speedrun=speedrun_status
    )
    db.add(new_ach)
    db.commit()
    
    return {
        "status": "success", 
        "message": f"Przyznano osiągnięcie: {achievement_name}",
        "saved_score": calculated_score,
        "is_speedrun": speedrun_status
    }

@app.get("/user-achievements/{username}")
def get_user_achievements(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")
    
    achievements = [
        {
            "name": ach.name, 
            "description": ach.description,
            "total_score": round(ach.total_score, 2),
            "is_speedrun": ach.is_speedrun
        } 
        for ach in user.achievements
    ]
    return {"username": user.username, "achievements": achievements}