"""Sub-agents exposed to the supervisor as tools.

Each sub-agent is a Claude conversation underneath. The contract is:
  async def run(state: FrameState, **inputs) -> SomeResult

The supervisor never reaches inside a sub-agent — it passes data in, gets data out.
"""
