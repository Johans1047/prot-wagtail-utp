from dataclasses import dataclass, field


@dataclass
class FAQItem:
    q: str
    a: str


@dataclass
class FAQCategory:
    title: str
    items: list[FAQItem] = field(default_factory=list)


@dataclass
class ImportantDate:
    title: str
    event_date: str
    description: str


@dataclass
class BackgroundItem:
    year_label: str
    description: str


@dataclass
class JicCategory:
    name: str
    description: str


@dataclass
class Award:
    prize: str
    year: str
    entity: str
    description: str
