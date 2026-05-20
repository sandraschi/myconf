import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contacts_substrate import Contact, ContactManager, LocalSystemProvider, WindowsContactProvider


class TestContacts:
    def test_contact_dataclass(self):
        c = Contact(id="1", name="Test User", email="test@example.com", source="manual")
        assert c.name == "Test User"
        assert c.email == "test@example.com"

    def test_contact_manager_init(self):
        mgr = ContactManager(cache_path="test_contacts_cache.json")
        assert mgr is not None
        assert len(mgr.search("anything")) == 0

    def test_contact_search(self):
        mgr = ContactManager(cache_path="test_contacts_cache.json")
        mgr.contacts = [
            Contact(id="1", name="Alice", email="alice@example.com", source="manual"),
            Contact(id="2", name="Bob", email="bob@test.com", company="Acme", source="manual"),
        ]
        assert len(mgr.search("alice")) == 1
        assert len(mgr.search("bob")) == 1
        assert len(mgr.search("acme")) == 1
        assert len(mgr.search("nonexistent")) == 0

    def test_contact_cache_persistence(self, tmp_path):
        cache = str(tmp_path / "contacts.json")
        mgr = ContactManager(cache_path=cache)
        mgr.contacts = [Contact(id="1", name="Test", email="t@t.com", source="manual")]
        mgr._save_cache()

        mgr2 = ContactManager(cache_path=cache)
        mgr2.load_cache()
        assert len(mgr2.contacts) == 1
        assert mgr2.contacts[0].name == "Test"

    def test_providers_defined(self):
        assert WindowsContactProvider is not None
        assert LocalSystemProvider is not None

    def teardown_method(self):
        import os

        for f in ["test_contacts_cache.json"]:
            if os.path.exists(f):
                os.remove(f)
