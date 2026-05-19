from fastapi import FastAPI
from sqlalchemy import text

from app.core.lifespan import lifespan
from app.database.exceptions import DatabaseError
from app.database.session import DbDependency

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check(db: DbDependency) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        raise DatabaseError("Could not connect to database") from e

    return {"status": "ok"}
