from Container.imports_library import *

def Format_Number(number: int):
    """Formats large numbers with suffixes"""
    if number >= 1e6:
        suffixes = ['Mill', 'Bill','Tril','Quad', 'Quin', 'Sext', 'Sept', 'Octi', 'Noni', 'Deci', 'Unde', 'Duod', 'Tred', 'Quat', 'Quin', 'Sexd', 'Sept', 'Octo', 'Nove', 'Vigi', 'Cent']
        index = int(math.log10(number) // 3 - 2)
        return f"{number / 10**(6 + index * 3):.2f} {suffixes[index]}" if index < len(suffixes) else f"{number:.2e}"
    return f"{number:,.2f}"