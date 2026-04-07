from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime, timedelta
import json

division_dict = {
    200 : "AL West",
    201 : "AL East",
    202 : "AL Central",
    203 : "NL West",
    204 : "NL East",
    205 : "NL Central"
}
espnTeamData = {}
teamsMapData = {}
teamsInfoData = {}
teamScheduleData = {}


def getEspnIdFromMlbId(mlbId):
    for team in teamsMapData["teams"]:
        if team["mlbId"] == mlbId:
            return team["espnId"]

def getEspnTeamObject(mlbId):
    id = str(getEspnIdFromMlbId(mlbId))
    for team in espnTeamData["sports"][0]["leagues"][0]["teams"]:
        if str(team["team"]["id"]) == id:
            return team["team"]

def formatStandingsJson(data):
    returnData = {}
    for division in data["records"]:
        returnData[division_dict[division["division"]["id"]]] = []
        for team in division["teamRecords"]:
            espnData = getEspnTeamObject(team["team"]["id"])
            teamInfo = {
                "id": team["team"]["id"],
                "wins": team["leagueRecord"]["wins"],
                "losses": team["leagueRecord"]["losses"],
                "slug": espnData["slug"],
                "abbreviation": espnData["abbreviation"],
                "displayName": espnData["displayName"],
                "name": espnData["name"],
                "location": espnData["location"],
                "color": espnData["color"],
                "alternateColor": espnData["alternateColor"],
                "logoImage": espnData["logos"][6]["href"] if (espnData["abbreviation"] != "PIT" and espnData["abbreviation"] != "BOS") else espnData["logos"][7]["href"]
            }
            returnData[division_dict[division["division"]["id"]]].append(teamInfo)
    return returnData

with open('testData/espnTeamData.json', 'r') as espnFile:
    espnTeamData = json.load(espnFile)

with open('testData/teamsMap.json', 'r') as teamsMapFile:
    teamsMapData = json.load(teamsMapFile)

with requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103&leagueId=104") as returnData: 
    data = formatStandingsJson(returnData.json())

with requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=" + datetime.now().strftime("%Y-%m-%d") + "&endDate=" + datetime.now().strftime("%Y-%m-%d")) as returnData:
    teamScheduleData = returnData.json()


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def homePage(request: Request):
    return templates.TemplateResponse(
        request=request, name="standings.html", context={"data": data, "teamScheduleData": teamScheduleData}
    )

@app.get("/team/{id}", response_class=HTMLResponse)
async def teamPage(request: Request, id: str):
    with requests.get("https://statsapi.mlb.com/api/v1/teams/" + id) as returnData:
        teamsInfoData = returnData.json()
    with requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=" + id + "&startDate=" + datetime.now().strftime("%Y-%m-%d") + "&endDate=" + (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")) as returnData:
        teamScheduleData = returnData.json()
    
    return templates.TemplateResponse(
        request=request, name="team.html", context={"teamsInfoData": teamsInfoData, "teamScheduleData": teamScheduleData}
    )
