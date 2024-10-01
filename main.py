from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

app = FastAPI()

class Fuel(BaseModel):
    gas: float = Field(alias="gas(euro/MWh)")
    kerosine: float = Field(alias="kerosine(euro/MWh)")
    co2: float = Field(alias="co2(euro/ton)")
    wind: float = Field(alias="wind(%)")

class PowerPlant(BaseModel):
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int

class ProductionPlanRequest(BaseModel):
    load: int
    fuels: Fuel
    powerplants: List[PowerPlant]

class ProductionPlanResponse(BaseModel):
    name: str
    p: float

@app.post("/productionplan", response_model=List[ProductionPlanResponse])
async def production_plan(request: ProductionPlanRequest):
    try:
        result = calculo_production_plan(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_cost(plant: Dict, fuels: Fuel) -> float:
    if plant['type'] == 'windturbine':
        return 0
    elif plant['type'] == 'gasfired':
        fuel_cost = fuels.gas / plant['efficiency']
        co2_cost = 0.3 * fuels.co2
        return fuel_cost + co2_cost
    elif plant['type'] == 'turbojet':
        return fuels.kerosine / plant['efficiency']

def calculo_production_plan(payload: ProductionPlanRequest) -> List[Dict[str, float]]:
    load = payload.load
    fuels = payload.fuels
    powerplants = [plant.dict() for plant in payload.powerplants]

    # Calcular el costo de cada planta
    for plant in powerplants:
        plant['cost'] = get_cost(plant, fuels)

    # Ordenar plantas por merit-order
    powerplants = sorted(powerplants, key=lambda x: x['cost'])

    remaining_load = load
    production_plan = []

    for plant in powerplants:
        pmin = plant['pmin']
        pmax = plant['pmax']

        if plant['type'] == 'windturbine':
            power = pmax * (fuels.wind / 100)
        else:
            if remaining_load >= pmin:
                if remaining_load <= pmax:
                    power = remaining_load
                else:
                    power = pmax
            else:
                # Evitar sobreproduccion
                power = 0
        
        production_plan.append({"name": plant['name'], "p": round(power, 1)})
        remaining_load -= power

        if remaining_load <= 0:
            break

    return production_plan
