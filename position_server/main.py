import datetime

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI(title="Trade Allocation Simulator Position Monitor")


@app.get("/")
async def root():
    return {"message": "Position monitor is running"}

@app.post("/position_send")
async def show_position(request: Request):
    position_tick = await request.json()
    print(f"New positions coming to position server are: {datetime.datetime.now()}: {position_tick}")
    return {"data": position_tick}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
