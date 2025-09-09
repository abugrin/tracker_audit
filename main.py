#!/usr/bin/env python3
"""
Yandex Tracker Audit Tool

A modern Python CLI tool for auditing Yandex Tracker queues and access permissions.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from config import ConfigManager, TrackerConfig
from audit import TrackerAuditor
from export import ExcelExporter
from translations import get_translator, t, Language
from logging_config import setup_logging, get_log_filename, log_api_statistics, log_audit_summary

# Initialize rich console
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="tracker-audit",
    help=t("app_help"),
    rich_markup_mode="rich"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


def initialize_translator():
    """Initialize translator with language from config."""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    if config and config.language:
        translator = get_translator()
        if config.language == "ru":
            translator.set_language(Language.RU)
        else:
            translator.set_language(Language.EN)


def ask_audit_scope() -> str:
    """Ask user for audit scope selection.
    
    Returns:
        Selected scope: 'groups', 'users', 'both', or 'all_users_group'
    """
    console.print(Panel.fit(
        Text.from_markup(t("audit_scope_selection_description")),
        title=t("audit_scope_selection_title"),
        border_style="blue"
    ))
    
    console.print(f"1. {t('audit_scope_all_users_group')}")
    console.print(f"2. {t('audit_scope_groups_only')}")
    console.print(f"3. {t('audit_scope_users_only')}")  
    console.print(f"4. {t('audit_scope_both')}")
    
    # Show warning about user permissions
    console.print(f"\n⚠️  {t('audit_scope_warning')}", style="yellow")
    
    choice = Prompt.ask(
        t("audit_scope_select"),
        choices=["1", "2", "3", "4"],
        default="1",
        show_choices=False
    )
    
    if choice == "1":
        return "all_users_group"
    elif choice == "2":
        return "groups"
    elif choice == "3":
        return "users"
    else:
        return "both"


def setup_configuration() -> Optional[TrackerConfig]:
    """Set up configuration interactively.
    
    Returns:
        TrackerConfig if successful, None otherwise
    """
    config_manager = ConfigManager()
    
    # Check if configuration already exists
    if config_manager.config_exists():
        config = config_manager.load_config()
        console.print(t("config_found_existing", path=config_manager.get_config_path()), style="green")
        
        # Show current config (masked token)
        masked_token = config.token[:8] + "..." + config.token[-4:] if len(config.token) > 12 else "***"
        console.print(t("config_token", token=masked_token))
        console.print(t("config_org_id", org_id=config.org_id))
        
        if not Confirm.ask(t("config_use_existing_question"), default=True):
            return setup_new_configuration(config_manager)
        
        return config
    else:
        console.print(t("config_not_found_setup"), style="yellow")
        return setup_new_configuration(config_manager)


def setup_new_configuration(config_manager: ConfigManager) -> Optional[TrackerConfig]:
    """Set up new configuration interactively.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        TrackerConfig if successful, None otherwise
    """
    # First, select language
    console.print(Panel.fit(
        Text.from_markup(t("config_setup_description")),
        title=t("config_setup_title"),
        border_style="blue"
    ))
    
    # Language selection
    console.print(f"1. {t('config_language_english')}")
    console.print(f"2. {t('config_language_russian')}")
    
    language_choice = Prompt.ask(
        t("config_select_language"),
        choices=["1", "2"],
        show_choices=False
    )
    
    if language_choice == "1":
        selected_language = "en"
        get_translator().set_language(Language.EN)
    else:
        selected_language = "ru" 
        get_translator().set_language(Language.RU)
    
    console.print()
    
    # Select organization type
    console.print(f"1. {t('config_org_type_360')}")
    console.print(f"2. {t('config_org_type_cloud')}")
    
    org_type_choice = Prompt.ask(
        t("config_select_org_type"),
        choices=["1", "2"],
        show_choices=False
    )
    
    if org_type_choice == "1":
        selected_org_type = "360"
        org_id_example = "8012334"
    else:
        selected_org_type = "cloud"
        org_id_example = "bpkftsa3daedasdfe4d"
    
    console.print()
    
    # Get OAuth token
    while True:
        token = Prompt.ask(
            f"\n{t('config_enter_token')}",
            password=True
        )
        
        if not token or len(token.strip()) < 10:
            console.print(t("config_invalid_token"), style="red")
            continue
        
        token = token.strip()
        break
    
    # Get Organization ID with validation based on type
    while True:
        org_id = Prompt.ask(
            f"{t('config_enter_org_id')} (e.g., {org_id_example})"
        )
        
        if not org_id or len(org_id.strip()) < 1:
            console.print(t("config_invalid_org_id"), style="red")
            continue
        
        org_id = org_id.strip()
        
        # Validate format based on organization type
        if selected_org_type == "360":
            # Yandex 360 - should be numeric
            if not org_id.isdigit():
                console.print(t("config_invalid_360_id"), style="red")
                continue
        else:
            # Cloud organization - should be alphanumeric string
            if len(org_id) < 10 or not org_id.replace('-', '').replace('_', '').isalnum():
                console.print(t("config_invalid_cloud_id"), style="red")
                continue
        
        break
    
    # Test configuration
    console.print(f"\n{t('config_testing')}", style="blue")
    
    try:
        test_config = TrackerConfig(token=token, org_id=org_id, org_type=selected_org_type, language=selected_language)
        auditor = TrackerAuditor(test_config.token, test_config.org_id, test_config.org_type)
        
        # Try to get queues to test connection
        test_queues = auditor.get_all_queues()  # Test the connection
        
        console.print(t("config_test_success"), style="green")
        
        # Save configuration
        config_manager.save_config(token, org_id, selected_org_type, selected_language)
        console.print(t("config_saved", path=config_manager.get_config_path()), style="green")
        
        return test_config
        
    except Exception as e:
        console.print(t("config_test_failed", error=str(e)), style="red")
        console.print(t("config_check_credentials"), style="yellow")
        
        if Confirm.ask(t("config_try_again"), default=True):
            return setup_new_configuration(config_manager)
        
        return None


@app.command()
def configure(
    reset: bool = typer.Option(False, "--reset", "-r", help=t("configure_reset_help"))
):
    """🔧 Configure OAuth token and organization ID."""
    initialize_translator()
    config_manager = ConfigManager()
    
    if reset or not config_manager.config_exists():
        config = setup_new_configuration(config_manager)
        if config:
            console.print(t("config_completed"), style="green bold")
        else:
            console.print(t("config_failed"), style="red")
            raise typer.Exit(1)
    else:
        config = config_manager.load_config()
        if config:
            # Update translator with config language
            if config.language == "ru":
                get_translator().set_language(Language.RU)
            
            masked_token = config.token[:8] + "..." + config.token[-4:] if len(config.token) > 12 else "***"
            console.print(t("config_current"))
            console.print(t("config_token", token=masked_token))
            console.print(t("config_org_id", org_id=config.org_id))
            console.print(t("config_file_location", path=config_manager.get_config_path()))


@app.command()
def audit(
    output: Optional[str] = typer.Option(None, "--output", "-o", help=t("audit_output_help")),
    show_summary: bool = typer.Option(True, "--summary/--no-summary", help=t("audit_summary_help")),
    scope: Optional[str] = typer.Option(None, "--scope", help=t("audit_scope_help"))
):
    """🔍 Audit all queues and their access permissions."""
    
    # Initialize translator first
    initialize_translator()
    
    # Load configuration
    config = setup_configuration()
    if not config:
        console.print(t("audit_config_required"), style="red")
        raise typer.Exit(1)
    
    # Set up output file path
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"tracker_audit_{timestamp}.xlsx"
    
    # Ask for audit scope if not provided
    if not scope:
        scope = ask_audit_scope()
    
    # Validate scope parameter
    valid_scopes = ["groups", "users", "both", "all_users_group"]
    if scope not in valid_scopes:
        console.print(f"❌ Invalid scope '{scope}'. Valid options: {', '.join(valid_scopes)}", style="red")
        raise typer.Exit(1)
    
    # Set up logging - full logging to file, only errors/warnings to console
    log_file = get_log_filename(output)
    setup_logging(log_file=log_file, log_level="INFO", console_output=True, console_level="ERROR")
    
    logger.info(f"Starting audit - Output: {output}, Log: {log_file}, Scope: {scope}")
    
    # Initialize auditor
    try:
        auditor = TrackerAuditor(config.token, config.org_id, config.org_type)
    except Exception as e:
        console.print(t("audit_init_failed", error=str(e)), style="red")
        raise typer.Exit(1)
    
    # Perform audit
    console.print(Panel.fit(
        t("audit_starting"),
        title=t("audit_started_title"),
        border_style="blue"
    ))
    
    try:
        audit_start_time = datetime.now()
        
        # Get all queues
        logger.info("Starting queue retrieval")
        queues = auditor.get_all_queues()
        if not queues:
            console.print(t("audit_no_queues"), style="red")
            logger.error("No queues found")
            raise typer.Exit(1)
        
        logger.info(f"Retrieved {len(queues)} queues")
        
        # Audit access permissions
        logger.info(f"Starting access permissions audit with scope: {scope}")
        access_info = auditor.audit_all_queues(scope=scope)
        logger.info(f"Found {len(access_info)} access entries")
        
        # Show summary if requested
        if show_summary:
            console.print("\n" + "="*60)
            auditor.display_summary()
            console.print("="*60)
            
            # Show access issues if any
            auditor.show_access_issues_summary()
        
        # Export to Excel
        output_path = Path(output)
        exporter = ExcelExporter()
        
        logger.info(f"Exporting results to {output_path}")
        success = exporter.export_audit_results(queues, access_info, output_path)
        
        if success:
            # Calculate elapsed time and log statistics
            audit_end_time = datetime.now()
            elapsed_time = (audit_end_time - audit_start_time).total_seconds()
            
            # Log audit summary
            log_audit_summary(len(queues), len(access_info), elapsed_time)
            
            # Log API statistics
            api_stats = auditor.api_client.get_statistics()
            log_api_statistics(api_stats)
            
            logger.info(f"Audit completed successfully - Output: {output_path}")
            
            console.print(Panel.fit(
                f"{t('audit_completed_success')}\n\n"
                f"{t('audit_results_exported', path=output_path.absolute())}\n"
                f"{t('audit_total_queues', count=len(queues))}\n"
                f"{t('audit_total_entries', count=len(access_info))}",
                title=t("audit_complete_title"),
                border_style="green"
            ))
        else:
            logger.error("Export failed")
            console.print(t("audit_export_failed"), style="yellow")
            raise typer.Exit(1)
            
    except KeyboardInterrupt:
        logger.info("Audit cancelled by user")
        console.print(f"\n{t('audit_cancelled')}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception(f"Audit failed with exception: {str(e)}")
        console.print(t("audit_failed", error=str(e)), style="red")
        raise typer.Exit(1)


@app.command()
def info():
    """ℹ️  Show information about the current configuration and tool."""
    initialize_translator()
    
    console.print(Panel.fit(
        Text.from_markup(t("tool_info_description")),
        title=t("tool_info_title"),
        border_style="blue"
    ))
    
    # Show current configuration status
    config_manager = ConfigManager()
    if config_manager.config_exists():
        config = config_manager.load_config()
        console.print(f"\n{t('config_ready')}")
        console.print(t("config_file_location", path=config_manager.get_config_path()))
        console.print(t("config_org_id", org_id=config.org_id))
    else:
        console.print(f"\n{t('config_not_setup')}")
        console.print(t("config_get_started"))


def main():
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print(f"\n{t('goodbye')}", style="blue")
        raise typer.Exit(0)


if __name__ == "__main__":
    main()
