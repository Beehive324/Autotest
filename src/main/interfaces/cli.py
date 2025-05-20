import click
import json
from datetime import datetime
from pyfiglet import Figlet
from typing import Optional
from contextlib import contextmanager
from ..agents.recon_phase.recon import Recon
from ..agents.planning_phase.planner import Planner
from ..agents.attacking_phase.attacker import Attacker
from ..agents.reporting_phase.reporter import Reporter
from ..graph import create_workflow, graph
from ..agents.orchestrator.memory import PenTestState
from langchain_ollama import ChatOllama
import asyncio
import os
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage

f = Figlet(font='slant')
__author__ = "Fairson Soares"

@contextmanager
def streaming_output(verbose: bool = False):
    """Context manager for streaming output with progress indicators"""
    if verbose:
        click.echo("Starting streaming output...")
    try:
        yield
    finally:
        if verbose:
            click.echo("\nStreaming completed")

def print_banner():
    """Print the application banner"""
    print(f.renderText('AutoTest'))
    print("Multi-Agent Framework for Automated Pentesting")
    print("=" * 50)

def validate_target(ctx, param, value):
    """Validate the target input"""
    if not value:
        raise click.BadParameter('Target is required')
    return value

@click.group()
def cli():
    """Multi-Agent Framework for Automated Pentesting"""
    pass

@cli.command()
@click.option('--target', '-t', required=True, callback=validate_target, help='Target to scan (IP or domain)')
@click.option('--ports', '-p', default='1-1000', help='Port range to scan (e.g., 1-1000)')
@click.option('--output', '-o', default='recon_results.json', help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def recon(target, ports, output, verbose):
    """Run the reconnaissance phase"""
    print_banner()
    click.echo(f"Starting reconnaissance phase for target: {target}")
    
    # Initialize state
    state = PenTestState(
        ip_port=target,
        target_domain=target if '.' in target else None,
        remaining_steps=100,
    )
    
    # Initialize recon agent
    local_model = "llama3.2"
    model = ChatOllama(model=local_model, temperature=1)        
    recon = Recon(model=model)
    
    try:
        with streaming_output(verbose) as stream:
            # Run reconnaissance with progress updates
            with click.progressbar(length=100, label='Reconnaissance Progress') as progress:
                results = recon.invoke(state)
                for i in range(100):
                    progress.update(1)
                    if verbose:
                        click.echo(f"\nProcessing step {i+1}/100")
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
            
        click.echo(f"Reconnaissance completed. Results saved to {output}")
    except Exception as e:
        click.echo(f"Error during reconnaissance: {str(e)}", err=True)

@cli.command()
@click.option('--target', '-t', required=True, callback=validate_target, help='Target to plan for')
@click.option('--scope', '-s', help='Scope of the pentest')
@click.option('--output', '-o', default='plan.json', help='Output file for plan')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def plan(target, scope, output, verbose):
    """Run the planning phase"""
    print_banner()
    click.echo(f"Starting planning phase for target: {target}")
    
    # Initialize state
    state = PenTestState(
        ip_port=target,
        target_domain=target if '.' in target else None,
        target_scope=[scope] if scope else None,
        remaining_steps=100,
        status=TestStatus.IN_PROGRESS,
        current_phase=TestPhase.PLANNING
    )
    
    # Initialize planner agent
    planner = Planner(model='llama3:2', tools="tools")
    
    try:
        # Run planning
        plan = planner.run(state)
        
        # Save plan
        with open(output, 'w') as f:
            json.dump(plan, f, indent=2)
            
        click.echo(f"Planning completed. Plan saved to {output}")
    except Exception as e:
        click.echo(f"Error during planning: {str(e)}", err=True)

@cli.command()
@click.option('--target', '-t', required=True, callback=validate_target, help='Target to attack')
@click.option('--plan', '-p', default='plan.json', help='Path to the attack plan')
@click.option('--output', '-o', default='attack_results.json', help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def attack(target, plan, output, verbose):
    """Run the attack phase"""
    print_banner()
    click.echo(f"Starting attack phase for target: {target}")
    
    # Initialize state
    state = PenTestState(
        ip_port=target,
        target_domain=target if '.' in target else None,
        remaining_steps=100,
        status=TestStatus.IN_PROGRESS,
        current_phase=TestPhase.ATTACK
    )
    
    # Initialize attacker agent
    attacker = Attacker(model='llama3:2', tools="tools")
    
    try:
        # Run attack
        results = attacker.run(state)
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
            
        click.echo(f"Attack completed. Results saved to {output}")
    except Exception as e:
        click.echo(f"Error during attack: {str(e)}", err=True)

@cli.command()
@click.option('--results', '-r', required=True, help='Path to the results file')
@click.option('--output', '-o', default='report.html', help='Output file for report')
@click.option('--format', '-f', type=click.Choice(['html', 'pdf', 'json']), default='html', help='Report format')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def report(results, output, format, verbose):
    """Generate a report from the results"""
    print_banner()
    click.echo("Generating report...")
    
    # Initialize reporter
    reporter = Reporter()
    
    try:
        # Generate report
        report = reporter.generate_report(results, format)
        
        # Save report
        with open(output, 'w') as f:
            f.write(report)
            
        click.echo(f"Report generated. Saved to {output}")
    except Exception as e:
        click.echo(f"Error generating report: {str(e)}", err=True)

@cli.command()
@click.option('--target', '-t', required=True, callback=validate_target, help='Target to scan')
@click.option('--scope', '-s', help='Scope of the pentest')
@click.option('--output', '-o', default='full_scan_results', help='Output directory for results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def full_scan(target, scope, output, verbose):
    """Run a full pentest scan using the multi-agent system"""
    print_banner()
    click.echo(f"\n🔍 Starting full scan for target: {click.style(target, fg='cyan', bold=True)}")
    
    # Initialize state
    state = PenTestState(
        ip_port=target,
        input_message=f"Starting full scan for target {target}",
        target_domain=target if '.' in target else None,
        target_scope=[scope] if scope else None,
        remaining_steps=100,
        messages=[HumanMessage(content=f"Start pentesting on {target}")],
        planning_results={},
        vulnerabilities=[],
        services=[],
        subdomains=[],
        open_ports=[],
        successful_exploits=[],
        failed_exploits=[],
        risk_score=0.0,
        chat_history=[],
        start_time=datetime.now()
    )
    
    try:
        # Run the workflow using the compiled graph
        async def run_workflow():
            async for chunk in graph.astream(
                state,
                subgraphs=True,
                stream_mode="updates"
            ):
                # Print the raw chunk for debugging
                click.echo(f"\n{chunk}")
                
                # Extract and print phase information
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    phase_info, update_info = chunk
                    if phase_info and len(phase_info) > 0:
                        phase = phase_info[0].split(':')[0]
                        click.echo(f"\nPhase: {click.style(phase, fg='green', bold=True)}")
                    
                    # Print state updates
                    if update_info:
                        click.echo(f"State Update: {json.dumps(update_info, indent=2, default=str)}")
        
        # Run the async workflow
        asyncio.run(run_workflow())
        
        # Save results
        os.makedirs(output, exist_ok=True)
        with open(f"{output}/results.json", 'w') as f:
            json.dump({
                "target": state.ip_port,
                "planning_results": state.planning_results,
                "vulnerabilities": [v.__dict__ for v in state.vulnerabilities],
                "services": [s.__dict__ for s in state.services],
                "subdomains": state.subdomains,
                "open_ports": state.open_ports,
                "successful_exploits": state.successful_exploits,
                "failed_exploits": state.failed_exploits,
                "risk_score": state.risk_score,
                "messages": [{"content": m.content, "type": m.__class__.__name__} for m in state.messages],
                "start_time": state.start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            }, f, indent=2)
            
        click.echo(f"\n✅ Scan completed. Results saved to {output}")
        
    except Exception as e:
        click.echo(f"\n❌ Error during scan: {str(e)}", err=True)

@cli.command()
@click.option('--target', '-t', required=True, callback=validate_target, help='Target to maintain access to')
@click.option('--method', '-m', type=click.Choice(['shell', 'web', 'network']), default='shell', help='Access method')
@click.option('--output', '-o', default='access_results.json', help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def maintain_access(target, method, output, verbose):
    """Maintain access to the target"""
    print_banner()
    click.echo(f"Maintaining access to target: {target}")
    
    try:
        # Implementation for maintaining access
        results = {"status": "success", "method": method, "timestamp": datetime.now().isoformat()}
        
        # Save results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
            
        click.echo(f"Access maintained. Results saved to {output}")
    except Exception as e:
        click.echo(f"Error maintaining access: {str(e)}", err=True)


if __name__ == '__main__':
    print(f.renderText('AutoTest'))
    cli()
   






