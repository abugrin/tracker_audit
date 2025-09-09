"""Configuration management for Tracker Audit Tool."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv


class TrackerConfig(BaseModel):
    """Configuration model for Yandex Tracker."""
    
    token: str = Field(..., description="OAuth token for Yandex Tracker API")
    org_id: str = Field(..., description="Organization ID")
    org_type: str = Field(..., description="Organization type: '360' or 'cloud'")
    base_url: str = Field(default="https://api.tracker.yandex.net", description="API base URL")
    language: str = Field(default="en", description="Interface language")


class ConfigManager:
    """Manages configuration for the Tracker Audit Tool."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_dir: Directory to store config files. Defaults to ~/.tracker_audit
        """
        if config_dir is None:
            config_dir = Path.home() / ".tracker_audit"
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.env_file = self.config_dir / ".env"
        
        # Load existing environment variables
        if self.env_file.exists():
            load_dotenv(self.env_file)
    
    def save_config(self, token: str, org_id: str, org_type: str, language: str = "en") -> None:
        """Save configuration to .env file.
        
        Args:
            token: OAuth token
            org_id: Organization ID
            org_type: Organization type ('360' or 'cloud')
            language: Interface language
        """
        env_content = f"""# Yandex Tracker Configuration
TRACKER_TOKEN={token}
TRACKER_ORG_ID={org_id}
TRACKER_ORG_TYPE={org_type}
TRACKER_LANGUAGE={language}
"""
        
        with open(self.env_file, "w") as f:
            f.write(env_content)
        
        # Reload environment
        load_dotenv(self.env_file, override=True)
    
    def load_config(self) -> Optional[TrackerConfig]:
        """Load configuration from environment.
        
        Returns:
            TrackerConfig if valid configuration exists, None otherwise
        """
        token = os.getenv("TRACKER_TOKEN")
        org_id = os.getenv("TRACKER_ORG_ID")
        org_type = os.getenv("TRACKER_ORG_TYPE", "360")  # Default to 360 for backward compatibility
        language = os.getenv("TRACKER_LANGUAGE", "en")
        
        if not token or not org_id:
            return None
        
        return TrackerConfig(token=token, org_id=org_id, org_type=org_type, language=language)
    
    def config_exists(self) -> bool:
        """Check if configuration file exists and is valid."""
        return self.env_file.exists() and self.load_config() is not None
    
    def get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        return self.env_file
