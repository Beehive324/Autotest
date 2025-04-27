from IPython.display import Image, display
from langgraph.graph imort StateGraph, START, END
from typing import TypedDict



#Recon Report summarisation
class Summary(TypedDict):
    cleaned_logs: List[Log]
    summary: str
    report: str
    processed_logs: List[str]

class SummarizationOutputState(TypedDict):
    report: str
    processed_logs: List[str]


def generate_summary(state):
    cleaned_logs = state['cleaned_logs']
    
    return {
        
        "processed_logs": [log for log in cleaned_logs]
    }


def print_report(state):
    summary = state["summary"]
    
    report = summary
    
    return {
        
        "report", report
    }


#for Failure Analysis
class FailureAnalysisSate(TypedDict):
    cleaned_logs: List[Log]
    failures: List[Log]
    fa_summary: str
    processed_logs: List[str]


class FailureAnalysisOutputState(TypedDict):
    fa_summary: str
    processed_logs: List[str]


def get_failures(state):
    cleaned_logs = state['cleaned_logs']
    failures = [log for log in cleaned_logs]
    
    return {
        
        "failures": failures
    }


def generate_summary(state):
    
    failures = state["failures"]
    
    return {
        
        "processed_logs": [f"failure-analysis-on-log-{failutr['id']}" for failure in failures]
    }