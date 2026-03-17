"""Unit tests for the AG-Visio contacts substrate."""

import pytest

from contacts_substrate import (
    MockGoogleContactProvider,
    MockOfficeProvider,
)


class TestContactManager:
    """Tests for the centralized ContactManager logic."""

    @pytest.mark.asyncio
    async def test_sync_all_populates_contacts(self, mock_contact_manager):
        """Verifies that syncing from all providers fills the unified list."""
        assert len(mock_contact_manager.contacts) == 0
        await mock_contact_manager.sync_all()
        assert len(mock_contact_manager.contacts) > 0

        # Verify diversity of sources
        sources = {c.source for c in mock_contact_manager.contacts}
        assert "office" in sources
        assert "windows" in sources
        assert "google" in sources

    def test_search_functionality(self, mock_contact_manager, sample_contacts):
        """Tests filtered retrieval of contacts."""
        mock_contact_manager.contacts = sample_contacts

        # Positive matches
        assert len(mock_contact_manager.search("Sandra")) == 1
        assert len(mock_contact_manager.search("GSD")) == 1

        # Case insensitivity
        assert len(mock_contact_manager.search("sandra")) == 1

        # Negative match
        assert len(mock_contact_manager.search("nonexistent")) == 0

    @pytest.mark.asyncio
    async def test_cache_persistence(self, mock_contact_manager, sample_contacts):
        """Standard verification of [MOCK] persistence substrate."""
        mock_contact_manager.contacts = sample_contacts
        mock_contact_manager._save_cache()

        # Create second manager pointing to same cache
        from contacts_substrate import ContactManager
        new_manager = ContactManager(cache_path=mock_contact_manager.cache_path)
        new_manager.load_cache()

        assert len(new_manager.contacts) == 2
        assert new_manager.contacts[0].name == "Sandra Test"


class TestProviders:
    """Tests for specific contact source providers."""

    @pytest.mark.asyncio
    async def test_office_provider_mock(self):
        provider = MockOfficeProvider()
        contacts = await provider.get_contacts()
        assert len(contacts) == 3
        assert any(c.name == "Steve Schipal" for c in contacts)

    @pytest.mark.asyncio
    async def test_google_provider_mock(self):
        provider = MockGoogleContactProvider()
        contacts = await provider.get_contacts()
        assert len(contacts) == 2
        assert any("Personal" in c.name for c in contacts)
