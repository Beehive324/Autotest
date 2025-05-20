from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from fpdf import FPDF
from datetime import datetime



class Report(BaseModel):
    report: str = Field(description="report to be written given pentest results")


class WriteReport(BaseTool):
    name: str = "Write Report Tool"
    description: str = "tool to write a report and generate PDF"
    args_schema: Type[BaseModel] = Report
    
    def _run(self, report: str) -> str:
        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Penetration Testing Report', ln=True, align='C')
        
        # Add timestamp
        pdf.set_font('Arial', 'I', 10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, f'Generated on: {timestamp}', ln=True, align='C')
        
        # Add report content
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, report)
        
        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pentest_report_{timestamp}.pdf"
        pdf.output(filename)
        
        return f"Report generated and saved as {filename}"
    
    async def _arun(self, report: str) -> str:
        return self._run(report)