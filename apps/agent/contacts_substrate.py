"""
apps/agent/contacts_substrate.py — Multi-provider Contact Manager
Tries real Windows contacts (COM), then falls back to cached/observed contacts.
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass

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


class WindowsContactProvider(ContactProvider):
    """Retrieves contacts from Windows Address Book via COM."""

    async def get_contacts(self) -> list[Contact]:
        try:
            import win32com.client  # pywin32

            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            contacts_folder = namespace.GetDefaultFolder(10)  # olFolderContacts
            items = contacts_folder.Items
            contacts = []
            for item in items:
                try:
                    contacts.append(
                        Contact(
                            id=f"outlook_{item.EntryID}",
                            name=f"{item.FirstName or ''} {item.LastName or ''}".strip(),
                            email=getattr(item, "Email1Address", None) or None,
                            phone=getattr(item, "BusinessTelephoneNumber", None)
                            or getattr(item, "MobileTelephoneNumber", None)
                            or None,
                            company=getattr(item, "CompanyName", None) or None,
                            source="windows",
                        )
                    )
                except Exception:
                    logger.debug("Failed to parse Windows contact item", exc_info=True)
                    continue
            if contacts:
                logger.info(f"Found {len(contacts)} contacts from Windows Address Book")
                return contacts
        except Exception as e:
            logger.debug(f"Windows Address Book unavailable: {e}")
        return []


class LocalSystemProvider(ContactProvider):
    """Extracts known users from the local Windows system."""

    async def get_contacts(self) -> list[Contact]:
        try:
            import win32net

            users = []
            resume = 0
            while True:
                data, _, _, resume = win32net.NetUserEnum(None, 0, 0, resume, 1024)
                for u in data:
                    name = u["name"]
                    if name not in ("Administrator", "Guest", "DefaultAccount"):
                        users.append(
                            Contact(
                                id=f"local_{name}",
                                name=name,
                                source="local_system",
                            )
                        )
                if resume == 0:
                    break
            logger.info(f"Found {len(users)} local system users")
            return users
        except Exception as e:
            logger.debug(f"Local system user enum unavailable: {e}")
        return []


class ContactManager:
    def __init__(self, cache_path: str = "contacts_cache.json"):
        self.providers: list[ContactProvider] = [
            WindowsContactProvider(),
            LocalSystemProvider(),
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
    logging.basicConfig(level=logging.INFO)
    manager = ContactManager()
    asyncio.run(manager.sync_all())
    print(f"Found {len(manager.contacts)} contacts.")
