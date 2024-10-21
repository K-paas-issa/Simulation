from fastapi import FastAPI, BackgroundTasks
from scheduler import scheduler
from contextlib import asynccontextmanager
import simulation_service
from fastapi import status
from fastapi import Response

app = FastAPI()


@app.get("/simulation")
def get_climate_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(simulation_service.simulation_start())
    return Response(status_code=status.HTTP_202_ACCEPTED)

@asynccontextmanager
async def lifespan(app: FastAPI): 
    yield
    scheduler.shutdown()

@app.get("/climate-data")
def simulation(object_name: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(simulation_service.simulation_body(), object_name)
    return Response(status_code=status.HTTP_202_ACCEPTED)