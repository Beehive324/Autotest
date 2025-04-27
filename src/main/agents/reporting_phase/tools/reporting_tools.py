from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type


class Report(BaseModel):
    report: str = Field(description="report to be written given pentest results")


class WriteReport(BaseTool):
    name = "Write Report Tool"
    description = "tool to write a report"
    args_schema: Type[BaseModel] = Report
    
    
    def _run(self, report: str) -> str:
        pass
    
    async def _arun(self, report: str) -> str:
        pass