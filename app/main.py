from fastapi import FastAPI, Depends, BackgroundTasks
from app.schemas.annuity import AnnuityCreate, AnnuityResponse
from app.services.annuity import calculate_premium
from app.dependencies import get_current_user, get_async_session, log_action
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.annuity import Annuity

app = FastAPI(title="FastAPI Spec-Driven Dev")

@app.post("/annuities/premium", response_model=AnnuityResponse)
async def create_annuity(
    annuity: AnnuityCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    premium = calculate_premium(annuity.principal, annuity.term_years, annuity.annual_rate)
    db_annuity = Annuity(
        principal=annuity.principal,
        term_years=annuity.term_years,
        annual_rate=annuity.annual_rate,
        premium=premium
    )
    session.add(db_annuity)
    await session.commit()
    await session.refresh(db_annuity)
    background_tasks.add_task(log_action, f"User {user['id']} created annuity: {premium}")
    return db_annuity