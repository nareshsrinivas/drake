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


    # string optimistic validation
    @model_validator(mode="before")
    @classmethod
    def validate_meaningful_input(cls, values):
        for value in values.values():
            # ignore booleans
            if isinstance(value, bool):
                continue
            # string validation
            if isinstance(value, str):
                cleaned = value.strip().lower()
                if cleaned and cleaned != "string":
                    return values
            # list validation
            if isinstance(value, list):
                cleaned_list = [
                    str(v).strip().lower()
                    for v in value
                    if str(v).strip() and str(v).strip().lower() != "string"
                ]
                if cleaned_list:
                    return values

        raise ValueError("Fill some information")

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


    class config:
        extra = "forbid"