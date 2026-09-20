import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, FiniteFloat, RootModel, field_validator

from controller.utils import Controller

controller = Controller()


@asynccontextmanager
async def lifespan(_app):
    tasks = [
        asyncio.create_task(controller.run_works()),
        asyncio.create_task(controller.send_data()),
    ]
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="Trade Allocation Simulator", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, error):
    details = [
        {
            key: item[key]
            for key in ("type", "loc", "msg")
            if key in item
        }
        for item in error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


class FillRequest(BaseModel):
    stock_ticker: str = Field(min_length=1)
    price: FiniteFloat = Field(gt=0)
    quantity: int = Field(gt=0)


class AllocationTargets(RootModel[dict[str, FiniteFloat]]):
    @field_validator("root")
    @classmethod
    def validate_targets(cls, targets):
        if not targets or any(not account for account in targets):
            raise ValueError("At least one named account is required")
        if any(weight < 0 for weight in targets.values()) or sum(targets.values()) <= 0:
            raise ValueError("Allocation weights must be non-negative and total above zero")
        return targets


@app.get("/")
async def root():
    return {"message": "Trade Allocation Simulator is running"}


@app.get("/positions")
async def positions():
    return controller.current_positions

@app.post("/fill")
async def update_fill(fill_request: FillRequest):
    fill_tick = fill_request.model_dump()
    controller.add_work(fill_tick)
    return {"message": "Success", "received_data_as_json": fill_tick}


@app.post("/aum")
async def update_aum(allocation_targets: AllocationTargets):
    aum_splits = allocation_targets.root
    controller.accounts_split = aum_splits
    controller.accounts_split_norm = controller.normalize_dict(aum_splits)
    return {"message": "Success", "received_data_as_json": aum_splits}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
