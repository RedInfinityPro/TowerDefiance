from Container.imports_library import *

def Format_Number(num):
    """Formats large numbers with suffixes"""
    if num >= 1e6:
        suffixes = ['Mill', 'Bill','Tril','Quad', 'Quin', 'Sext', 'Sept', 'Octi', 'Noni', 'Deci', 'Unde', 'Duod', 'Tred', 'Quat', 'Quin', 'Sexd', 'Sept', 'Octo', 'Nove', 'Vigi', 'Cent']
        index = int(math.log10(num) // 3 - 2)
        return f"{num / 10**(6 + index * 3):.2f} {suffixes[index]}" if index < len(suffixes) else f"{num:.2e}"
    return f"{num:,.2f}"