import re

regex = r"^[A-Z][^ @]* [A-Z][^ @]*@(Anima|Asura|Belias|Chocobo|Hades|Ixion|Mandragora|Masamune|Pandaemonium|Shinryu|Titan)$"
checker = re.compile(regex)

def is_vaild_nickname(nickname) -> bool:
    matches = checker.match(nickname)
    if matches is None:
        return False
    else:
        return True