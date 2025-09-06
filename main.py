from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import crud, models, schemas, auth
from database import SessionLocal, engine, Base

app = FastAPI()

@app.on_event("startup")
def on_startup():
    # This will try to create tables on startup.
    # If the database is not ready, it might fail, but the app will still start.
    if engine is None:
        print("!!! DATABASE ENGINE NOT CREATED. SKIPPING TABLE CREATION.")
        return
    try:
        Base.metadata.create_all(bind=engine)
        print("--- Database tables checked/created successfully.")
    except Exception as e:
        print(f"!!! Error creating database tables: {e}")

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database connection is not configured correctly.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        # The dependency `get_db` itself tries to create a session.
        # If this endpoint returns, it means a session was created.
        db.execute('SELECT 1')
        return {"status": "db_connection_successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI chat backend!"}

@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_message(db=db, message=message, user_id=current_user.id)

@app.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    return messages
