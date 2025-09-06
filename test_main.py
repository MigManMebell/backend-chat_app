from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Test application is running successfully!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
