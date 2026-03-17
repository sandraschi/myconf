import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contacts_substrate")


@dataclass
class Contact:
    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    source: str = "unknown"
    avatar_url: str | None = None


class ContactProvider:
    async def get_contacts(self) -> list[Contact]:
        raise NotImplementedError


class MockOfficeProvider(ContactProvider):
    """MOCK: Simulates Microsoft Graph API contact retrieval."""

    async def get_contacts(self) -> list[Contact]:
        # [MOCK] Simulating API latency
        await asyncio.sleep(0.5)
        return [
            Contact(
                id="off_1",
                name="Steve Schipal",
                email="steve@bank-it.at",
                company="Bank IT",
                source="office",
            ),
            Contact(
                id="off_2", name="Marion Hollabrunn", email="marion@family.at", source="office"
            ),
            Contact(id="off_3", name="Reinhard Hollabrunn", source="office"),
        ]


class WindowsLocalProvider(ContactProvider):
    """Simulates or retrieves local Windows contacts."""

    async def get_contacts(self) -> list[Contact]:
        # In a real implementation, this would use pywin32 or pywinrt
        # For now, providing high-fidelity mock data corresponding to the user's circle
        return [
            Contact(
                id="win_1", name="Benny (GSD)", source="windows", avatar_url="/avatars/benny.jpg"
            ),
            Contact(
                id="win_2", name="TMW TechLAB Service", email="service@tmw.at", source="windows"
            ),
        ]


class MockGoogleContactProvider(ContactProvider):
    """MOCK: Simulates Google People API contact retrieval."""

    async def get_contacts(self) -> list[Contact]:
        await asyncio.sleep(0.3)
        return [
            Contact(
                id="goog_1",
                name="Sandra Schipal (Personal)",
                email="sandra.schipal@gmail.com",
                source="google",
            ),
            Contact(
                id="goog_2",
                name="Japan Residency Support",
                email="tokyo.desk@google.com",
                source="google",
                company="Google Japan",
            ),
        ]


class ContactManager:
    def __init__(self, cache_path: str = "contacts_cache.json"):
        self.providers: list[ContactProvider] = [
            MockOfficeProvider(),
            WindowsLocalProvider(),
            MockGoogleContactProvider(),
        ]
        self.cache_path = cache_path
        self.contacts: list[Contact] = []

    async def sync_all(self):
        logger.info("Syncing contacts from all providers...")
        all_contacts = []
        for provider in self.providers:
            try:
                contacts = await provider.get_contacts()
                all_contacts.extend(contacts)
            except Exception as e:
                logger.error(f"Error syncing from {provider.__class__.__name__}: {e}")

        self.contacts = all_contacts
        self._save_cache()
        logger.info(f"Sync complete. Total contacts: {len(self.contacts)}")
        return self.contacts

    def search(self, query: str) -> list[Contact]:
        query = query.lower()
        return [
            c
            for c in self.contacts
            if query in c.name.lower()
            or (c.email and query in c.email.lower())
            or (c.company and query in c.company.lower())
        ]

    def _save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump([asdict(c) for c in self.contacts], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save contacts cache: {e}")

    def load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path) as f:
                    data = json.load(f)
                    self.contacts = [Contact(**c) for c in data]
            except Exception as e:
                logger.error(f"Failed to load contacts cache: {e}")


if __name__ == "__main__":
    # Test execution
    manager = ContactManager()
    asyncio.run(manager.sync_all())
    print(f"Found {len(manager.contacts)} contacts.")
    results = manager.search("Steve")
    for r in results:
        print(f"Match: {r.name} ({r.source})")
