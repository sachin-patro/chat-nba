from rich.console import Console
from rich.text import Text
import pyfiglet

console = Console()

def print_banner():
    ascii_banner = pyfiglet.figlet_format("CHAT NBA", font="block")
    banner_lines = ascii_banner.splitlines()
    width = max(len(line) for line in banner_lines)
    border = "═" * width
    console.print(f"[bold #1D428A]{border}[/bold #1D428A]")
    for line in banner_lines:
        styled_line = Text()
        for char in line:
            if char != " ":
                styled_line.append(char, style="bold #1D428A")
            else:
                styled_line.append(char)
        console.print(styled_line)
    console.print(f"[bold #1D428A]{border}[/bold #1D428A]")
