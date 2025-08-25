from pydantic import BaseModel, Field

class AnnuityCreate(BaseModel):
    principal: float = Field(..., gt=0, description="Initial investment amount")
    term_years: int = Field(..., ge=1, le=30, description="Term in years")
    annual_rate: float = Field(..., gt=0, le=100, description="Annual interest rate (%)")

class AnnuityResponse(AnnuityCreate):
    id: int
    premium: float