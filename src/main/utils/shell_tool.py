import logging
import platform
import subprocess
import warnings
from typing import Any, List, Optional, Type, Union
from pydantic import BaseModel, Field, root_validator

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)

from langchain_core.pydantic_v1 import BaseModel, Field, root_validator
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

#allow our agent to execute commands from the terminal

#Shell tools for the agent to use 

class ShellInput(BaseModel):
    command: str = Field(decription="Command to be executed")
    
    
class ShellTool(BaseTool):
    name: str = Field(default="ShellTool", description="Tool to execute shell commands")
    description: str = Field(default="Tool to execute shell commands")
    args_schema: Type[BaseModel] = ShellInput
    
    def _run(self, command: str) -> str:
        pass

class Nmap(BaseTool):
    pass

class MassScan(BaseTool):
    pass


