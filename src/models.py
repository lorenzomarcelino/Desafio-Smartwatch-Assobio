from pydantic import BaseModel, Field

# Modelo para INSERÇÃO (POST)
class PatientInput(BaseModel):
    Person_ID: int
    Gender: str
    Age: int
    Occupation: str
    # O 'le=24' garante validação automática
    Sleep_Duration: float = Field(alias="Sleep Duration", le=24, gt=0) 
    Quality_of_Sleep: int = Field(alias="Quality of Sleep", ge=1, le=10)
    Physical_Activity_Level: int = Field(alias="Physical Activity Level")
    Stress_Level: int = Field(alias="Stress Level", ge=1, le=10)
    BMI_Category: str = Field(alias="BMI Category")
    Blood_Pressure: str = Field(alias="Blood Pressure")
    Heart_Rate: int = Field(alias="Heart Rate")
    Daily_Steps: int = Field(alias="Daily Steps")
    Sleep_Disorder: str | None = Field(default="No", alias="Sleep Disorder")

# Modelo para PREDIÇÃO (ML)
class PredictionInput(BaseModel):
    age: int
    gender: str          
    sleep_duration: float
    bmi_category: str    
    heart_rate: int
    daily_steps: int
    blood_pressure: str 
    quality_of_sleep: int 
    physical_activity_level: int
    stress_level: int