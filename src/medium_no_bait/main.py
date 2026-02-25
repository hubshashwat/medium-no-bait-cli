import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import box
from rich.text import Text

# Ensure shared and feature folders are in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .author_updates.tracker import UpdatesTracker
from .shared.models import Article
from .shared.storage import Storage

console = Console()
storage = Storage()

def show_home():
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]Medium No-Bait CLI[/bold cyan]\n"
        "[white]Your distraction-free terminal reader[/white]",
        box=box.DOUBLE,
        border_style="bright_blue"
    ))
    
    # Show Summary
    authors = storage.get_authors()
    pubs = storage.get_publications()
    keywords = storage.get_keywords()

    summary_table = Table(box=box.SIMPLE, show_header=False)
    summary_table.add_column("Key", style="bold cyan")
    summary_table.add_column("Value")
    summary_table.add_row("Authors", f"{len(authors)} favorites")
    summary_table.add_row("Publications", f"{len(pubs)} followed")
    summary_table.add_row("Keywords", f"{len(keywords)} active" if keywords else "None")
    
    # Calculate most recent check across all targets
    all_dates = []
    for a in authors:
        dt = storage.get_last_access(a, type="authors")
        if dt: all_dates.append(dt)
    for p in pubs:
        dt = storage.get_last_access(p, type="publications")
        if dt: all_dates.append(dt)
    
    if all_dates:
        latest = max(all_dates).strftime("%b %d, %H:%M")
        summary_table.add_row("Last Check", f"[dim]{latest}[/dim]")
    else:
        summary_table.add_row("Last Check", "[dim]Never[/dim]")
    
    console.print(Panel(summary_table, title="[bold green]Configuration Summary[/bold green]", expand=False))

def manage_favorites():
    while True:
        console.clear()
        console.print(Panel("[bold magenta]Manage Favorites & Filters[/bold magenta]", border_style="magenta"))
        console.print("1. [cyan]Manage Authors[/cyan]")
        console.print("2. [green]Manage Publications[/green]")
        console.print("3. [yellow]Manage Keywords[/yellow]")
        console.print("4. [white]Back to Main Menu[/white]")
        
        choice = Prompt.ask("Select category", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            manage_list("authors")
        elif choice == "2":
            manage_list("publications")
        elif choice == "3":
            manage_keywords()
        else:
            break

def manage_list(type_name):
    while True:
        console.clear()
        console.print(Panel(f"[bold]Manage {type_name.title()}[/bold]", border_style="blue"))
        
        items = storage.get_authors() if type_name == "authors" else storage.get_publications()
        if items:
            for idx, item in enumerate(items, 1):
                last_date = storage.get_last_access(item, type=type_name)
                date_str = last_date.strftime("%Y-%m-%d") if last_date else "Never"
                console.print(f"{idx}. {item} [dim](Last: {date_str})[/dim]")
        else:
            console.print("[dim]Empty list.[/dim]")

        console.print("\na. [green]Add[/green] | r. [red]Remove[/red] | b. [yellow]Back[/yellow]")
        action = Prompt.ask("Action", choices=["a", "r", "b"])
        
        if action == "a":
            new_item = Prompt.ask(f"Enter {type_name} name")
            if type_name == "authors":
                storage.add_author(new_item)
            else:
                storage.add_publication(new_item)
            console.print(f"[green]Added {new_item}[/green]")
        elif action == "r":
            if not items: continue
            idx_to_rem = IntPrompt.ask("Enter number to remove", choices=[str(i) for i in range(1, len(items)+1)])
            item_to_rem = items[idx_to_rem-1]
            if type_name == "authors":
                storage.remove_author(item_to_rem)
            else:
                storage.remove_publication(item_to_rem)
            console.print(f"[red]Removed {item_to_rem}[/red]")
        else:
            break

def manage_keywords():
    while True:
        console.clear()
        console.print(Panel("[bold yellow]Manage Keyword Filters[/bold yellow]", border_style="yellow"))
        
        keywords = storage.get_keywords()
        if keywords:
            for idx, kw in enumerate(keywords, 1):
                console.print(f"{idx}. {kw}")
        else:
            console.print("[dim]No keywords defined. Results will not be filtered.[/dim]")

        console.print("\na. [green]Add[/green] | r. [red]Remove[/red] | b. [yellow]Back[/yellow]")
        action = Prompt.ask("Action", choices=["a", "r", "b"])
        
        if action == "a":
            new_kw = Prompt.ask("Enter keyword to track")
            storage.add_keyword(new_kw)
        elif action == "r":
            if not keywords: continue
            idx_to_rem = IntPrompt.ask("Enter number to remove", choices=[str(i) for i in range(1, len(keywords)+1)])
            storage.remove_keyword(keywords[idx_to_rem-1])
        else:
            break

def handle_updates(apply_keywords=False):
    authors = storage.get_authors()
    pubs = storage.get_publications()
    keywords = storage.get_keywords() if apply_keywords else []
    
    if not authors and not pubs:
        console.print("[yellow]Please add some favorite authors or publications first![/yellow]")
        input("\nPress Enter...")
        return

    if apply_keywords and not keywords:
        console.print("[yellow]No keywords defined. Please add keywords in 'Manage Favorites' first.[/yellow]")
        input("\nPress Enter...")
        return

    console.clear()
    title_text = "Keyword Hits" if apply_keywords else "Full Updates Feed"
    console.print(Panel(f"[bold green]{title_text}[/bold green]", border_style="green"))
    
    # Refine the prompt to be clearer about "specific" categories
    source_choice = Prompt.ask(
        f"Which sources to check for {title_text}?", 
        choices=["all", "authors", "pubs"], 
        default="all"
    )
    
    use_last = Prompt.ask("Check since last visit?", choices=["y", "n"], default="y")
    fetch_limit = IntPrompt.ask("History depth (1-10 stories per source)", default=5)
    fetch_limit = max(1, min(10, fetch_limit))

    limit_date = None
    if use_last == "n":
        from datetime import timedelta
        default_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_input = Prompt.ask(f"Check stories after date (YYYY-MM-DD)", default=default_date)
        try:
            limit_date = datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            limit_date = datetime.now() - timedelta(days=7)

    all_updates = []
    
    with console.status("[bold green]Fetching new stories..."):
        # Authors
        if source_choice in ["all", "authors"]:
            for auth in authors:
                l_date = limit_date or storage.get_last_access(auth, type="authors") or datetime(2026, 1, 1)
                tracker = UpdatesTracker([auth], target_type="authors")
                all_updates.extend(tracker.get_updates_after(l_date, update_timestamp=True, limit=fetch_limit, keywords=keywords))
        
        # Publications
        if source_choice in ["all", "pubs"]:
            for pub in pubs:
                l_date = limit_date or storage.get_last_access(pub, type="publications") or datetime(2026, 1, 1)
                tracker = UpdatesTracker([pub], target_type="publications")
                all_updates.extend(tracker.get_updates_after(l_date, update_timestamp=True, limit=fetch_limit, keywords=keywords))

    if not all_updates:
        console.print(f"\n[yellow]No new stories found matching your {('keyword ' if apply_keywords else '')}criteria.[/yellow]")
        input("\nPress Enter to return to menu...")
        return

    all_updates.sort(key=lambda x: x.pub_date, reverse=True)

    console.print(f"\n[bold green]{title_text} Results:[/bold green]\n")

    for idx, art in enumerate(all_updates, 1):
        # Header line: Date | Source | Title
        header = f"[blue]{art.pub_date.strftime('%b %d')}[/blue] | [green]{art.author[:15]}[/green] | [white bold]{art.title}[/white bold]"
        
        # Link line: Printed clearly for terminal clickability
        link_line = f"[cyan underline]{art.link}[/cyan underline]"
        
        # We use a simple vertical layout which is MUCH safer for links than a table
        console.print(header)
        console.print(link_line, soft_wrap=True)
        console.print("") # Spacer

    console.print(f"[dim]Found {len(all_updates)} stories. Timestamps updated.[/dim]")
    input("\nPress Enter to return to menu...")

def main():
    while True:
        show_home()
        console.print("\n[bold]Choose an option:[/bold]")
        console.print("1. [green]Full Updates Feed[/green] (Check All Favorites)")
        console.print("2. [bold yellow]Keyword Hits[/bold yellow] (High-Signal Filtered Feed)")
        console.print("3. [magenta]Manage Favorites[/magenta] (Authors, Pubs, Keywords)")
        console.print("4. [dim]Exit[/dim]")
        
        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            handle_updates(apply_keywords=False)
        elif choice == "2":
            handle_updates(apply_keywords=True)
        elif choice == "3":
            manage_favorites()
        elif choice == "4":
            console.print("[yellow]Goodbye![/yellow]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Exiting...[/yellow]")
        sys.exit(0)
