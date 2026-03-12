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


@dataclass
class EventIntro:
    title: str
    main_description: str
    secondary_description: str
    framework_label: str = "En el marco de"
    framework_text: str = ""
    logo_fallback_text: str = "Logo del evento"
    is_active: bool = True


@dataclass
class Coordinator:
    university_short_name: str
    name: str
    email: str
    sort_order: int = 0
    is_active: bool = True
    photo: str = None

    @property
    def shortName(self):
        return self.university_short_name

    @property
    def coordinator(self):
        return self.name


@dataclass
class OrganizerCommitteeMember:
    name: str
    role: str
    institution: str
    sort_order: int = 0
    is_active: bool = True
    photo: str = None
