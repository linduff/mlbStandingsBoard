from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import json

division_dict = {
    200 : "AL West",
    201 : "AL East",
    202 : "AL Central",
    203 : "NL West",
    204 : "NL East",
    205 : "NL Central"
}

def formatStandingsJson(data):
    returnData = {}
    for division in data["records"]:
        returnData[division_dict[division["division"]["id"]]] = []
        for team in division["teamRecords"]:
            returnData[division_dict[division["division"]["id"]]].append(team["team"]["name"] + " (" + str(team["leagueRecord"]["wins"]) + "-" + str(team["leagueRecord"]["losses"]) + ")")
    return returnData

# with open('testData/standings-return.json', 'r') as file:
    # returnData = json.load(file)
with requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103&leagueId=104") as returnData:
    data = formatStandingsJson(returnData.json())

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="standings.html", context={"data": data}
    )
