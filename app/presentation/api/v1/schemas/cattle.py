from pydantic import BaseModel, ConfigDict, Field


class CattleDataCreate(BaseModel):
    cattle_id: int = Field(description="Linked cattle entity ID.")
    lat: float = Field(description="Latitude in decimal degrees.", examples=[-23.5505])
    lon: float = Field(description="Longitude in decimal degrees.", examples=[-46.6333])
    movement: float = Field(description="Movement index reported by the sensor.", ge=0)
    temperature: float = Field(description="Body or ambient temperature in °C.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cattle_id": 1,
                "lat": -23.5505,
                "lon": -46.6333,
                "movement": 12.5,
                "temperature": 38.2,
            }
        }
    )


class CattleDataResponse(CattleDataCreate):
    id: int = Field(description="Telemetry record ID.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 10,
                "cattle_id": 1,
                "lat": -23.5505,
                "lon": -46.6333,
                "movement": 12.5,
                "temperature": 38.2,
            }
        },
    )
