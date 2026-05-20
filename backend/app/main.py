from fastapi import FastAPI

app = FastAPI(title="AI Financial Research Assistant API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
