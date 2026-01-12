import pandas as pd
import joblib
import sqlite3
import os
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from pathlib import Path

# --- CONFIGURAÇÃO DE CAMINHOS ---
# BASE_DIR aponta para a raiz do projeto (/app no Docker)
BASE_DIR = Path(__file__).resolve().parent.parent 
MODEL_PATH = BASE_DIR / "analysis" / "model_health.pkl"
DATA_PATH = BASE_DIR / "data" / "cleaned_health_data.csv" 
DB_PATH = BASE_DIR / "health.db"

# Variável global para o modelo
model = None

# --- CICLO DE VIDA (STARTUP RIGOROSO) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Startup da Aplicação...")
    
    # 1. Carregar Modelo
    global model
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ERRO CRÍTICO: Modelo não encontrado em {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print("Modelo carregado.")

    # 2. Carregar Dados (Obrigatório)
    if not DATA_PATH.exists():
        # DEBUG: Se não achar, mostra o que tem na pasta para entender o erro
        print(f"ERRO CRÍTICO: CSV não encontrado em {DATA_PATH}")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Conteúdo da raiz ({BASE_DIR}):")
        for f in BASE_DIR.iterdir():
            print(f" - {f.name}")
        if (BASE_DIR / "data").exists():
             print(f"Conteúdo de 'data':")
             for f in (BASE_DIR / "data").iterdir():
                 print(f" - {f.name}")
                 
        raise FileNotFoundError(f"O sistema exige o arquivo {DATA_PATH} para iniciar.")

    # 3. Popular Banco de Dados
    try:
        df = pd.read_csv(DATA_PATH)
        # Limpeza dos nomes das colunas
        df.columns = [c.replace(' ', '_') for c in df.columns]
        
        conn = sqlite3.connect(str(DB_PATH))
        # if_exists="replace" garante que o banco seja recriado com os dados do CSV
        df.to_sql("patients", conn, if_exists="replace", index=False)
        
        # Verifica se gravou mesmo
        cursor = conn.cursor()
        count = cursor.execute("SELECT count(*) FROM patients").fetchone()[0]
        conn.close()
        
        print(f"Banco de dados populado com sucesso! Total de pacientes: {count}")
        
    except Exception as e:
        print(f"Falha fatal ao popular o banco: {str(e)}")
        raise e # Quebra a aplicação se o banco falhar
    
    yield

app = FastAPI(title="Health API", lifespan=lifespan)

# --- SCHEMAS ---

# Modelo para INSERÇÃO (POST)
class PatientInput(BaseModel):
    Person_ID: int
    Gender: str
    Age: int
    Occupation: str
    # REQUISITO: "Validar Sleep Duration não permitir > 24 horas"
    # O 'le=24' (less or equal) garante isso automaticamente
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

# --- ENDPOINTS OPERACIONAIS (CRUD) ---

# 1. POST - Inserir Paciente
@app.post("/patients", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientInput):
    try:
        # 1. Validação e Transformação da Pressão Arterial
        try:
            # Quebra "120/80" em duas variáveis
            systolic_str, diastolic_str = patient.Blood_Pressure.split('/')
            systolic = int(systolic_str)
            diastolic = int(diastolic_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de pressão arterial inválido. Use 'SIS/DIA' (ex: 120/80).")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 2. Verifica se ID já existe
        cursor.execute("SELECT Person_ID FROM patients WHERE Person_ID = ?", (patient.Person_ID,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail=f"Paciente com ID {patient.Person_ID} já existe.")

        # 3. Prepara o Dicionário para o Banco
        # Pega os dados brutos
        raw_data = patient.model_dump(by_alias=True)
        
        # Converte chaves com espaço para underscore (ex: "Sleep Duration" -> "Sleep_Duration")
        # Isso é necessário para bater com a maioria das colunas
        db_data = {k.replace(' ', '_'): v for k, v in raw_data.items()}

        # --- A CORREÇÃO MÁGICA AQUI ---
        # Remove a chave "Blood_Pressure" que não existe no banco
        if "Blood_Pressure" in db_data:
            del db_data["Blood_Pressure"]
        
        # Adiciona as duas colunas que REALMENTE existem
        db_data["Systolic_BP"] = systolic
        db_data["Diastolic_BP"] = diastolic
        # ------------------------------

        # 4. Monta a Query Dinâmica com os dados corrigidos
        cols = ", ".join(db_data.keys())
        placeholders = ", ".join(["?"] * len(db_data))
        values = tuple(db_data.values())
        
        sql = f"INSERT INTO patients ({cols}) VALUES ({placeholders})"
        
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        
        return {"message": "Paciente criado com sucesso", "patient": db_data}

    except HTTPException as he:
        raise he
    except Exception as e:
        # Dica: Printar o erro no console ajuda a debugar erros de SQL
        print(f"Erro SQL: {e}") 
        raise HTTPException(status_code=500, detail=f"Erro ao inserir: {str(e)}")

# 2. GET - Buscar Paciente por ID
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    conn = sqlite3.connect(str(DB_PATH))
    # Importante: O Pandas carrega linhas como 'Row', precisamos converter para dict
    # Usando row_factory do sqlite3 é mais leve que carregar pandas aqui
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE Person_ID = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

# 3. DELETE - Remover Paciente
@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Verifica se existe antes de tentar deletar
    cursor.execute("SELECT Person_ID FROM patients WHERE Person_ID = ?", (patient_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Paciente não encontrado para exclusão")
        
    cursor.execute("DELETE FROM patients WHERE Person_ID = ?", (patient_id,))
    conn.commit()
    conn.close()
    return # 204 No Content não retorna corpo

# --- ENDPOINT ANALÍTICO ---
@app.get("/analytics/insights")
def get_insights():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        # Lê a tabela inteira para um DataFrame para facilitar a manipulação
        df = pd.read_sql("SELECT * FROM patients", conn)
        conn.close()

        # --- 1. Insight: Pressão Alta x Estresse ---
        # "A pressão alta está ligada a um alto nível de estresse"
        # Lógica: Agrupar por Nível de Estresse e ver a média da Pressão Sistólica
        insight_stress_bp = (
            df.groupby("Stress_Level")["Systolic_BP"]
            .mean()
            .round(1)
            .to_dict()
        )

        # --- 2. Insight: Gênero x Qualidade do Sono ---
        # "Mulheres tem uma qualidade do sono maior que os homens"
        # Lógica: Média da qualidade agrupada por Gênero
        insight_gender_quality = (
            df.groupby("Gender")["Quality_of_Sleep"]
            .mean()
            .round(2)
            .to_dict()
        )

        # --- 3. Insight: Idade x Qualidade do Sono ---
        # "Tendência da qualidade do sono melhorar com a idade"
        # Lógica: Agrupar por Idade e tirar média da qualidade.
        insight_age_trend = (
            df.groupby("Age")["Quality_of_Sleep"]
            .mean()
            .round(2)
            .to_dict()
        )

        # --- 4. Insight: Pressão Média por Distúrbio ---
        # "Pessoas com pressão alta tem grandes chances de ter algum distúrbio do sono"
        # Aqui mostramos a média de pressão sistólica agrupada pelo tipo de distúrbio.
        insight_bp_by_disorder = (
            df.groupby("Sleep_Disorder")["Systolic_BP"]
            .mean()
            .round(1)
            .sort_values(ascending=False) # Ordena do maior para o menor (mais grave primeiro)
            .to_dict()
        )

        # --- 5. Insight: Idade x Distúrbios ---
        # "Problemas no sono tendem a aparecer nos mais velhos"
        # Lógica: Média de idade agrupada por Tipo de Distúrbio
        insight_disorder_age = (
            df.groupby("Sleep_Disorder")["Age"]
            .mean()
            .round(1)
            .to_dict()
        )

        # --- 6. Insight: Apneia/Insônia x Atividade Física ---
        # "Apneia tem maior atividade física, Insônia tem menor"
        insight_disorder_activity = (
            df.groupby("Sleep_Disorder")["Physical_Activity_Level"]
            .mean()
            .round(1)
            .sort_values(ascending=False) # Ordena para mostrar quem é maior
            .to_dict()
        )

        return {
            "stress_vs_blood_pressure": insight_stress_bp,
            "gender_sleep_quality": insight_gender_quality,
            "age_quality_trend": insight_age_trend,
            "average_bp_by_disorder": insight_bp_by_disorder, 
            "average_age_by_disorder": insight_disorder_age,
            "activity_level_by_disorder": insight_disorder_activity
        }

    except Exception as e:
        print(f"Erro analítico: {e}")
        raise HTTPException(status_capiode=500, detail=str(e))

# --- ENDPOINT PREDIÇÃO ---
@app.post("/predict/sleep-disorder")
def predict_disorder(data: PredictionInput):
    if not model:
        raise HTTPException(status_code=500, detail="Modelo não carregado")

    try:
        # 1. Tratamento de Gênero
        gender_encoded = 1 if data.gender.lower() == "male" else 0
        
        # 2. Tratamento de BMI
        bmi_encoded = 1 if "normal" in data.bmi_category.lower() else 0
        
        # 3. Tratamento de Pressão
        try:
            systolic = int(data.blood_pressure.split('/')[0])
        except:
            systolic = 120

        # 4. Vetor Final
        features = [[
            data.age,              
            data.sleep_duration,    
            data.heart_rate,        
            data.daily_steps,      
            systolic,               
            gender_encoded,         
            bmi_encoded             
        ]]
        
        prediction = model.predict(features)
        return {"prediction": str(prediction[0])}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na predição: {str(e)}")