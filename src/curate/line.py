from dataclasses import dataclass
from typing import FrozenSet

@dataclass(frozen=True)
class Line:
    number: int               # Radnummer
    text: str                 # Textinnehåll (ingen newline)
    kinds: FrozenSet[str]     # Typ av rad (t.ex. code, doc, comment)

    def with_kind(self, kind: str) -> "Line":
        # Lägg till ett nytt semantiskt tag till linjen
        if kind in self.kinds:
            return self
        return Line(self.number, self.text, frozenset(self.kinds | {kind}))
