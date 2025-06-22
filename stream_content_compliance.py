"""
stream_content_compliance.py

Streams content compliance analysis for multiple markdown files using PydanticAI.
Checks for violence, sexual content, or self-harm violations.
"""

import asyncio
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel
from rich.console import Console
from rich.live import Live
from rich.table import Table

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class Category(str, Enum):
    violence = "violence"
    sexual = "sexual"
    self_harm = "self_harm"


class ContentCompliance_response(BaseModel):
    is_violating: bool
    category: Optional[Category]
    explanation_if_violating: Optional[str]


async def analyze_content(agent: Agent, filename: str, content: str) -> tuple[str, ContentCompliance_response]:
    """Analyze a single markdown file for content compliance"""
    prompt = f"""Analyze the following markdown file '{filename}' for content compliance.
Check if it contains any violations in these categories:
- violence: content depicting or promoting violence
- sexual: sexual or adult content
- self_harm: content related to self-harm or harmful behaviors

Content to analyze:

{content}

Respond with whether it violates any guidelines, and if so, which category and why."""

    async with agent.run_stream(prompt) as result:
        async for message, last in result.stream_structured(debounce_by=0.01):
            if last:
                validated_result = await result.validate_structured_output(message)
                return filename, validated_result


async def main():
    console = Console()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY not found in environment variables or .env file![/red]")
        console.print("Please create a .env file with:")
        console.print("OPENAI_API_KEY=your-api-key-here")
        console.print("OPENAI_BASE_URL=your-base-url-here (optional)")
        return
    
    # Get base URL if provided
    base_url = os.getenv("OPENAI_BASE_URL")
    
    # Check if sample_md folder exists
    md_folder = Path("sample_md")
    if not md_folder.exists():
        console.print("[red]Error: 'sample_md' folder not found![/red]")
        console.print("Please create a 'sample_md' folder with your markdown files.")
        return
    
    # Find all markdown files
    md_files = list(md_folder.glob("*.md"))
    if not md_files:
        console.print("[red]Error: No markdown files found in 'sample_md' folder![/red]")
        return
    
    console.print(f"[cyan]Found {len(md_files)} markdown files to analyze[/cyan]")
    
    # Read all markdown files
    file_contents = {}
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            file_contents[md_file.name] = content
        except Exception as e:
            console.print(f"[red]Error reading {md_file.name}: {e}[/red]")
    
    if not file_contents:
        console.print("[red]No files could be read successfully![/red]")
        return
    
    # Create agent with custom base URL if provided
    console.print("[cyan]Initializing Content Compliance Agent...[/cyan]")
    if base_url:
        console.print(f"[cyan]Using custom base URL: {base_url}[/cyan]")
        model_name = f'azure.gpt-4o'
    else:
        model_name = 'azure.gpt-4o'
    

    model = OpenAIModel(model_name)
    agent = Agent(
        model,
        output_type=ContentCompliance_response,
        output_type_instructions="Analyze content for policy violations carefully. Only mark as violating if content clearly contains violence, sexual content, or self-harm related material."
    )
    
    # Process files with live updates
    results = {}
    
    with Live(console=console, refresh_per_second=4) as live:
        # Create initial table
        table = Table(
            title="Content Compliance Analysis - Live Stream",
            caption=f"Analyzing {len(file_contents)} files...",
            show_lines=True
        )
        table.add_column("File", style="cyan", width=25)
        table.add_column("Status", style="bold", width=15)
        table.add_column("Category", style="yellow", width=15)
        table.add_column("Explanation", style="white", width=50)
        
        live.update(table)
        
        # Create tasks for concurrent processing
        tasks = [
            analyze_content(agent, filename, content)
            for filename, content in file_contents.items()
        ]
        
        # Process as they complete
        completed = 0
        for coro in asyncio.as_completed(tasks):
            try:
                filename, compliance_result = await coro
                results[filename] = compliance_result
                completed += 1
                
                # Recreate table with updated results
                table = Table(
                    title="Content Compliance Analysis - Live Stream",
                    caption=f"Completed {completed}/{len(file_contents)} files",
                    show_lines=True
                )
                table.add_column("File", style="cyan", width=25)
                table.add_column("Status", style="bold", width=15)
                table.add_column("Category", style="yellow", width=15)
                table.add_column("Explanation", style="white", width=50)
                
                # Add all results so far
                for fname in sorted(results.keys()):
                    result = results[fname]
                    status = "[red]❌ Violating[/red]" if result.is_violating else "[green]✅ Compliant[/green]"
                    category = result.category.value if result.category else "—"
                    explanation = result.explanation_if_violating or "No violations found"
                    
                    # Truncate filename if too long
                    display_fname = fname if len(fname) <= 25 else fname[:22] + "..."
                    
                    # Truncate explanation if too long
                    if len(explanation) > 50:
                        explanation = explanation[:47] + "..."
                    
                    table.add_row(display_fname, status, category, explanation)
                
                live.update(table)
                
            except Exception as e:
                console.print(f"[red]Error processing file: {e}[/red]")
    
    # Convert to DataFrame
    console.print("\n[green]Creating DataFrame...[/green]")
    
    # Prepare data for DataFrame
    df_data = []
    for filename, result in results.items():
        df_data.append({
            'filename': filename,
            'is_violating': result.is_violating,
            'category': result.category.value if result.category else None,
            'explanation': result.explanation_if_violating
        })
    
    df = pd.DataFrame(df_data)
    
    # Display summary statistics
    console.print("\n[cyan]Compliance Summary:[/cyan]")
    console.print(f"Total files analyzed: {len(df)}")
    console.print(f"Compliant files: {len(df[~df['is_violating']])}")
    console.print(f"Violating files: {len(df[df['is_violating']])}")
    
    if df['is_violating'].any():
        console.print("\n[red]Violations by category:[/red]")
        violations = df[df['is_violating']]['category'].value_counts()
        for category, count in violations.items():
            console.print(f"  - {category}: {count}")
    
    # Show the full DataFrame
    console.print("\n[cyan]Full Results DataFrame:[/cyan]")
    console.print(df.to_string())
    
    # Save to CSV
    output_file = f"compliance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_file, index=False)
    console.print(f"\n[green]Results saved to: {output_file}[/green]")


if __name__ == "__main__":
    asyncio.run(main())