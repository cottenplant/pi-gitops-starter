from fastapi import FastAPI

app = FastAPI(title="example-app")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
