from pydantic import BaseModel

class AgencyProfileStatusResponse(BaseModel):
    agency_profile: bool
    agency_status: str