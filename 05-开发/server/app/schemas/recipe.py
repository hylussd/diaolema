"""配方 Schema。"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class RecipeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    pressure_min: int = Field(..., ge=800, le=1100)
    pressure_max: int = Field(..., ge=800, le=1100)
    water_temp_min: float = Field(..., ge=-10.0, le=50.0)
    water_temp_max: float = Field(..., ge=-10.0, le=50.0)
    fish_species: str = Field(..., min_length=1, max_length=32)
    spot_type: str | None = Field(None, max_length=16)
    is_public: bool = Field(default=False)

    @field_validator("pressure_max")
    @classmethod
    def pressure_max_ge_min(cls, v, info):
        if "pressure_min" in info.data and v < info.data["pressure_min"]:
            raise ValueError("pressure_max must be >= pressure_min")
        return v

    @field_validator("water_temp_max")
    @classmethod
    def water_temp_max_ge_min(cls, v, info):
        if "water_temp_min" in info.data and v < info.data["water_temp_min"]:
            raise ValueError("water_temp_max must be >= water_temp_min")
        return v


class RecipeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    pressure_min: int | None = Field(None, ge=800, le=1100)
    pressure_max: int | None = Field(None, ge=800, le=1100)
    water_temp_min: float | None = Field(None, ge=-10.0, le=50.0)
    water_temp_max: float | None = Field(None, ge=-10.0, le=50.0)
    fish_species: str | None = Field(None, min_length=1, max_length=32)
    spot_type: str | None = Field(None, max_length=16)
    is_public: bool | None = None


class RecipeResponse(BaseModel):
    id: int
    user_id: int | None = None  # 公开配方匿名，不返回
    name: str
    pressure_min: int
    pressure_max: int
    water_temp_min: float
    water_temp_max: float
    fish_species: str
    spot_type: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
