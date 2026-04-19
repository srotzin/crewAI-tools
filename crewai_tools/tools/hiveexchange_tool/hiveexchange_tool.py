"""
HiveExchange CrewAI Tools — prediction markets, spot trading, genesis feed.
Drop into any CrewAI agent to give it access to 233 live prediction markets.

Install: pip install crewai requests
Usage:
    from hiveexchange_crewai import hiveexchange_tools
    agent = Agent(tools=hiveexchange_tools(did="did:hive:your-did"), ...)
"""
from crewai.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field
import requests, json

EXCHANGE_URL = "https://hiveexchange-service.onrender.com"

class HiveMarketsInput(BaseModel):
    category: Optional[str] = Field(None, description="Category filter: ai_benchmarks, blockchain, hive_native, agent_infrastructure, zk_benchmarks, compliance, stablecoin")
    limit: Optional[int] = Field(20, description="Max markets to return")

class HiveBetInput(BaseModel):
    market_id: str = Field(..., description="Market ID e.g. pm_223")
    side: str = Field(..., description="YES or NO")
    amount_usdc: float = Field(..., description="Bet size in USDC")
    did: str = Field(..., description="Your Hive DID (did:hive:...)")

class HiveExchangeMarketsTool(BaseTool):
    name: str = "Browse HiveExchange Markets"
    description: str = (
        "Browse 233 live prediction markets on HiveExchange — the only A2A-native "
        "prediction market. Categories: AI benchmarks, blockchain events, agent infrastructure, "
        "Hive network growth (pm_200/223/228/233), ZK benchmarks (pm_202/229), compliance. "
        "Returns current YES/NO pools, odds, and volume."
    )

    def _run(self, category: Optional[str] = None, limit: int = 20) -> str:
        params = {"limit": limit}
        if category:
            params["category"] = category
        r = requests.get(f"{EXCHANGE_URL}/v1/exchange/predict/markets", params=params, timeout=10)
        return json.dumps(r.json(), indent=2) if r.ok else f"Error: {r.text[:200]}"

class HiveExchangeBetTool(BaseTool):
    name: str = "Place HiveExchange Prediction Bet"
    description: str = (
        "Place a YES or NO bet on any HiveExchange prediction market. "
        "Get a free DID first: POST https://hivegate.onrender.com/v1/gate/onboard. "
        "Fee: 10bps taker, -8bps maker (you get paid to make markets). "
        "Yield vault: deposit idle USDC to earn 5.1% APY while waiting to bet."
    )

    def _run(self, market_id: str, side: str, amount_usdc: float, did: str) -> str:
        r = requests.post(
            f"{EXCHANGE_URL}/v1/exchange/predict/markets/{market_id}/bet",
            json={"side": side.upper(), "amount_usdc": amount_usdc, "did": did},
            headers={"x-hive-did": did, "Content-Type": "application/json"},
            timeout=10,
        )
        return json.dumps(r.json(), indent=2)

class HiveGenesisFeedTool(BaseTool):
    name: str = "HiveExchange Genesis Agent Feed"
    description: str = (
        "Watch what HiveExchange's 6 autonomous Genesis agents are trading right now. "
        "Agents: Spread Tightener, Hive Ambassador, Compliance Oracle, Simpson Strong Agent, "
        "Yield Optimizer, ZK Benchmarker. Real-time signal for market direction."
    )

    def _run(self, limit: int = 10) -> str:
        r = requests.get(f"{EXCHANGE_URL}/v1/exchange/genesis/feed", params={"limit": limit}, timeout=10)
        return json.dumps(r.json(), indent=2) if r.ok else f"Error: {r.text[:200]}"

def hiveexchange_tools(did: str = "") -> list:
    """Return all HiveExchange CrewAI tools."""
    return [HiveExchangeMarketsTool(), HiveExchangeBetTool(), HiveGenesisFeedTool()]

if __name__ == "__main__":
    t = HiveExchangeMarketsTool()
    print(t._run(category="hive_native"))
