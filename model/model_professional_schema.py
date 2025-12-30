from pydantic import BaseModel, model_validator
from typing import Optional, List

class ModelProfessionalSchema(BaseModel):
    professional_experience: bool
    experience_details: Optional[str] = None

    languages: Optional[List[str]] = None
    other_languages: Optional[List[str]] = None

    skills: Optional[List[str]] = None
    other_skills: Optional[List[str]] = None

    interested_categories: Optional[List[str]] = None
    other_interested_categories: Optional[List[str]] = None

    willing_to_travel: Optional[bool] = None

    @model_validator(mode="after")
    def validate_experience(self):
        if self.professional_experience is True:
            if not self.experience_details:
                raise ValueError(
                    "experience_details is required when professional_experience is true"
                )
        else:
            self.experience_details = None

        return self


