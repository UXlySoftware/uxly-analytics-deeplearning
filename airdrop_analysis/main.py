from typing import Optional, List
import json
from fastapi import FastAPI, HTTPException , Query , Request
from fastapi.responses import HTMLResponse , JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from airdrop_analyzer import AirdropAnalyzer
from data_handler.models.base_models.query_parameters import \
    GraphQueryParameters, ClaimersGraphParameters
from data_handler.models.query_models.community_query import CommunityQuery
from data_handler.models.query_models.graph_query import GraphQuery

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
AirdropAnalyzer()

async def get_data_from_request(request):
    content_type = request.headers.get('Content-Type')
    if content_type is None:
        raise HTTPException(status_code=400, detail='No Content-Type provided')
    elif content_type == 'application/json':
        try:
            return await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail='Invalid JSON data')
    else:
        raise HTTPException(status_code=400, detail='Content-Type not supported')
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/claimers_graph/{token}/{airdrop}/{season}")
def visualize_claimers_graph(
    token: str, 
    airdrop: str, 
    season: str,
    from_date: Optional[str] = '2023-12-01T00:00:00Z',
    to_date: Optional[str] = '2024-06-01T00:00:00Z',
    claimers: Optional[int] = 1,
    parent_depth: Optional[int] = 2,
    child_depth: Optional[int] = 2,
    edge_limit: Optional[int] = 3,
    edge_order: Optional[str] = 'DESC',
    partition: Optional[bool] = False,
    ) -> HTMLResponse:
    param = ClaimersGraphParameters(
        token=token,
        airdrop=airdrop,
        season=season,
        from_date=from_date,
        to_date=to_date,
        claimer_limit=claimers,
        parent_depth=parent_depth,
        child_depth=child_depth,  
        edge_limit=edge_limit,
        edge_order=edge_order,
        partition=partition,
        )
    graph = AirdropAnalyzer().get_claimers_graph(param)
    return HTMLResponse(content=graph, status_code=200)

@app.api_route("/distribution_graph/",methods=["GET","POST"])
async def visualize_distribution_graph(
    request: Request
    ) -> HTMLResponse:
    data = await get_data_from_request(request)
    query_data = GraphQuery.create_from_json(data)
    param = GraphQueryParameters(
        center_addresses=query_data.distributor_addresses,
        chain=query_data.chain,
        contract_addresses=query_data.contract_addresses,
        from_date=query_data.from_date,
        to_date=query_data.to_date,
        parent_depth=query_data.parent_depth,
        child_depth=query_data.child_depth,  
        edge_limit=query_data.edge_limit,
        edge_order=query_data.edge_order,
        partition=query_data.partition,
        user_id=query_data.user_id
        )
    graph = AirdropAnalyzer().get_distribution_graph(param)
    return HTMLResponse(content=graph, status_code=200)

@app.api_route("/distribution_graph_json/",methods=["GET","POST"])
async def distribution_graph_json(
    request: Request
    ) -> HTMLResponse:
    data = await get_data_from_request(request)
    query_data = GraphQuery.create_from_json(data)
    param = GraphQueryParameters(
        center_addresses=query_data.distributor_addresses,
        chain=query_data.chain,
        contract_addresses=query_data.contract_addresses,
        from_date=query_data.from_date,
        to_date=query_data.to_date,
        parent_depth=query_data.parent_depth,
        child_depth=query_data.child_depth,  
        edge_limit=query_data.edge_limit,
        edge_order=query_data.edge_order,
        partition=query_data.partition,
        user_id=query_data.user_id
    )
    graph = AirdropAnalyzer().get_distribution_graph_json(param)
    return JSONResponse(content=graph, status_code=200)

@app.api_route("/graph_records/",methods=["GET","POST"])
async def get_graph_records(
    request: Request
    ) -> HTMLResponse:
    data = await get_data_from_request(request)
    return AirdropAnalyzer().get_graph_records_from_user_id(data["user_id"])

@app.api_route("/get_communities/",methods=["GET","POST"])
async def get_communities(
    request: Request
    ) -> dict:
    data = await get_data_from_request(request)
    query_data = CommunityQuery.create_from_json(data)
    param = GraphQueryParameters(
    center_addresses= query_data.distributor_addresses,
    chain=query_data.chain,
    contract_addresses=query_data.contract_addresses,
    from_date=query_data.from_date,
    to_date=query_data.to_date,
    parent_depth=query_data.parent_depth,
    child_depth=query_data.child_depth,  
    edge_limit=query_data.edge_limit,
    edge_order=query_data.edge_order,
    partition=True,
    user_id=query_data.user_id
    )
    return AirdropAnalyzer().get_communities(param)

@app.get("/distribution_graph_for_fast_api/")
def visualize_distribution_graph(
    distributor_addresses: List[str] = Query(...),
    contract_addresses: List[str] = Query(...),
    chain: Optional[str] = 'base',
    from_date: Optional[str] = '2023-12-01T00:00:00Z',
    to_date: Optional[str] = '2024-06-01T00:00:00Z',
    parent_depth: Optional[int] = 1,
    child_depth: Optional[int] = 1,
    edge_limit: Optional[int] = 1,
    edge_order: Optional[str] = 'DESC',
    partition: Optional[bool] = False,
    user_id: Optional[str] = ""
    ) -> HTMLResponse:
    param = GraphQueryParameters(
        center_addresses=distributor_addresses,
        chain=chain,
        contract_addresses=contract_addresses,
        from_date=from_date,
        to_date=to_date,
        parent_depth=parent_depth,
        child_depth=child_depth,  
        edge_limit=edge_limit,
        edge_order=edge_order,
        partition=partition,
        user_id=user_id
        )
    graph = AirdropAnalyzer().get_distribution_graph(param)
    return HTMLResponse(content=graph, status_code=200)

@app.get("/distribution_graph_json_for_fast_api/")
def json_distribution_graph(
    distributor_addresses: List[str] = Query(...),
    contract_addresses: List[str] = Query(...),
    chain: Optional[str] = 'base',
    from_date: Optional[str] = '2023-12-01T00:00:00Z',
    to_date: Optional[str] = '2024-06-01T00:00:00Z',
    parent_depth: Optional[int] = 1,
    child_depth: Optional[int] = 1,
    edge_limit: Optional[int] = 1,
    edge_order: Optional[str] = 'DESC',
    partition: Optional[bool] = False,
    user_id: Optional[str] = ""
    ) -> HTMLResponse:
    param = GraphQueryParameters(
        center_addresses=distributor_addresses,
        chain=chain,
        contract_addresses=contract_addresses,
        from_date=from_date,
        to_date=to_date,
        parent_depth=parent_depth,
        child_depth=child_depth,  
        edge_limit=edge_limit,
        edge_order=edge_order,
        partition=partition,
        user_id=user_id
        )
    graph = AirdropAnalyzer().get_distribution_graph_json(param)
    return JSONResponse(content=graph, status_code=200)

@app.get("/graph_records_for_fast_api/")
def get_graph_records(
    user_id : str
) -> JSONResponse:
    return AirdropAnalyzer().get_graph_records_from_user_id(user_id)

@app.get("/get_communities_for_fastapi/")
def get_communities(
    distributor_addresses: List[str] = Query(...),
    contract_addresses: List[str] = Query(...),
    chain: Optional[str] = 'base',
    from_date: Optional[str] = '2023-12-01T00:00:00Z',
    to_date: Optional[str] = '2024-06-01T00:00:00Z',
    parent_depth: Optional[int] = 1,
    child_depth: Optional[int] = 1,
    edge_limit: Optional[int] = 1,
    edge_order: Optional[str] = 'DESC',
    user_id: Optional[str] = ''
    ) -> dict:
    param = GraphQueryParameters(
        center_addresses=distributor_addresses,
        chain=chain,
        contract_addresses=contract_addresses,
        from_date=from_date,
        to_date=to_date,
        parent_depth=parent_depth,
        child_depth=child_depth,  
        edge_limit=edge_limit,
        edge_order=edge_order,
        partition=True,
        user_id=user_id
        )
    return AirdropAnalyzer().get_communities(param)

@app.get("/get_graph_summary/")
def get_graph_summary(
    distributor_address: str,
    contract_address: str,
    chain: Optional[str] = 'base',
    from_date: Optional[str] = '2023-12-01T00:00:00Z',
    to_date: Optional[str] = '2024-06-01T00:00:00Z',
    parent_depth: Optional[int] = 1,
    child_depth: Optional[int] = 1,
    edge_limit: Optional[int] = 1,
    edge_order: Optional[str] = 'DESC',
    partition: Optional[bool] = False,
    ) -> dict:
    param = GraphQueryParameters(
        center_addresses=[distributor_address],
        chain=chain,
        contract_addresses=[contract_address],
        from_date=from_date,
        to_date=to_date,
        parent_depth=parent_depth,
        child_depth=child_depth,  
        edge_limit=edge_limit,
        edge_order=edge_order,
        partition=partition,
        )
    return AirdropAnalyzer().get_graph_summary(param)
