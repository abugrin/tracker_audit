"""Translation support for Tracker Audit Tool."""

from typing import Dict, Any
from enum import Enum


class Language(Enum):
    """Supported languages."""
    EN = "en"
    RU = "ru"


class Translator:
    """Handles translations for the application."""
    
    def __init__(self, language: Language = Language.EN):
        """Initialize translator with specified language.
        
        Args:
            language: Language to use for translations
        """
        self.language = language
        self._translations = TRANSLATIONS
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key to the current language.
        
        Args:
            key: Translation key
            **kwargs: Variables to substitute in the translation
            
        Returns:
            Translated string with variables substituted
        """
        try:
            translation = self._translations[self.language.value][key]
            if kwargs:
                return translation.format(**kwargs)
            return translation
        except KeyError:
            # Fallback to English if translation not found
            try:
                translation = self._translations[Language.EN.value][key]
                if kwargs:
                    return translation.format(**kwargs)
                return translation
            except KeyError:
                # Return key if no translation found
                return key
    
    def set_language(self, language: Language):
        """Set the current language.
        
        Args:
            language: Language to set
        """
        self.language = language


# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # CLI Messages
        "app_help": "🔍 Yandex Tracker Audit Tool - Audit queues and access permissions",
        "configure_help": "🔧 Configure OAuth token and organization ID.",
        "audit_help": "🔍 Audit all queues and their access permissions.",
        "info_help": "ℹ️  Show information about the current configuration and tool.",
        
        # Configuration
        "config_found": "✅ Found existing configuration at: {path}",
        "config_token": "   Token: {token}",
        "config_org_id": "   Org ID: {org_id}",
        "config_use_existing": "Do you want to use the existing configuration?",
        "config_not_found": "🔧 No configuration found. Let's set it up!",
        "config_setup_title": "🔐 Setup Required",
        "config_setup_description": """[bold blue]Yandex Tracker API Configuration[/bold blue]

To use this tool, you need:
1. [bold]OAuth Token[/bold]: Get it from https://oauth.yandex.com/
2. [bold]Organization ID[/bold]: Found in your Tracker organization settings

[yellow]Note:[/yellow] Your credentials will be stored securely in ~/.tracker_audit/.env""",
        "config_enter_token": "[bold]Enter your OAuth token[/bold]",
        "config_enter_org_id": "[bold]Enter your Organization ID[/bold]",
        "config_select_org_type": "[bold]Select organization type[/bold]",
        "config_org_type_360": "Yandex 360 for Business (numeric ID, e.g., 8015133)",
        "config_org_type_cloud": "Yandex Cloud Organization (string ID, e.g., bpfstkj3gi1dfd2s5d4d)",
        "config_select_language": "[bold]Select language / Выберите язык[/bold]",
        "config_language_english": "English",
        "config_language_russian": "Русский",
        "config_invalid_token": "❌ Invalid token. Please enter a valid OAuth token.",
        "config_invalid_org_id": "❌ Invalid organization ID. Please enter a valid ID.",
        "config_testing": "🧪 Testing configuration...",
        "config_test_success": "✅ Configuration test successful!",
        "config_saved": "✅ Configuration saved to: {path}",
        "config_test_failed": "❌ Configuration test failed: {error}",
        "config_check_credentials": "Please check your token and organization ID.",
        "config_try_again": "Do you want to try again?",
        "config_completed": "🎉 Configuration completed successfully!",
        "config_failed": "❌ Configuration failed.",
        "config_required": "❌ Configuration required. Run 'configure' command first.",
        "config_current": "✅ Current configuration:",
        "config_file_location": "   Config file: {path}",
        
        # Audit Process
        "audit_started": "🔍 Starting comprehensive audit of Yandex Tracker",
        "audit_title": "Audit Started",
        "fetching_queues": "🔍 Fetching all queues...",
        "queues_loaded": "✅ Successfully loaded {count} queues",
        "auditing_permissions": "🔐 Auditing queue access permissions...",
        "auditing_queue": "  Auditing {queue}...",
        "auditing_queue_with_progress": "Auditing {queue} [{current}/{total}]",
        "audit_complete_summary": "✅ Audited {queues} queues, found {entries} access entries",
        "no_queues_found": "❌ No queues found or failed to fetch queues.",
        "audit_cancelled": "❌ Audit cancelled by user.",
        "audit_failed": "❌ Audit failed: {error}",
        "audit_failed_export": "⚠️  Audit completed but export failed.",
        
        # Export
        "exporting_excel": "📊 Exporting audit results to Excel...",
        "export_success": "✅ Audit results exported to: {path}",
        "export_failed": "❌ Error exporting to Excel: {error}",
        
        # Results
        "queue_summary": "📊 Queue Summary",
        "access_summary": "📈 Access Summary:",
        "total_access_entries": "  • Total access entries: {count}",
        "subject_type_count": "  • {type}: {count} entries",
        "audit_complete_title": "🎉 Audit Complete",
        "audit_results": """✅ Audit completed successfully!

📊 Results exported to: [bold]{path}[/bold]
📈 Total queues audited: [bold]{queues}[/bold]
🔐 Total access entries: [bold]{entries}[/bold]""",
        
        # Info
        "tool_info_title": "📋 Tool Information",
        "tool_info_description": """[bold blue]Yandex Tracker Audit Tool[/bold blue]

[bold]Purpose:[/bold]
This tool audits Yandex Tracker queues and their access permissions,
providing comprehensive reports in Excel format.

[bold]Features:[/bold]
• 🔍 Audit all queues in your organization
• 🔐 Review access permissions and user assignments
• 📊 Export detailed results to Excel

[bold]Commands:[/bold]
• [cyan]configure[/cyan] - Set up OAuth token and organization ID
• [cyan]audit[/cyan] - Run comprehensive audit
• [cyan]info[/cyan] - Show this information""",
        "config_ready": "✅ Configuration: Ready",
        "config_not_setup": "⚠️  Configuration: Not set up",
        "config_get_started": "Run [bold cyan]configure[/bold cyan] command to get started",
        "goodbye": "👋 Goodbye!",
        
        # Table Headers
        "queue_key": "Queue Key",
        "name": "Name",
        "lead": "Lead",
        "access_entries": "Access Entries",
        "description": "Description",
        "default_type": "Default Type",
        "default_priority": "Default Priority",
        
        # Progress Messages
        "loading_queues": "Loading queues...",
        "found_queues": "Found {count} queues",
        "loaded_queues": "✅ Loaded {count} queues",
        
        # Error Messages
        "error_fetching_queues": "❌ Error fetching queues: {error}",
        "error_initializing_auditor": "❌ Failed to initialize auditor: {error}",
        "could_not_get_users": "Could not get users: {error}",
        "could_not_get_groups": "Could not get groups: {error}",
        "could_not_get_permissions": "Could not get permissions for {type} {id} in queue {queue}: {error}",
        "could_not_audit_queue": "Could not audit permissions for queue {queue}: {error}",
        
        # Additional untranslated strings
        "config_found_existing": "✅ Found existing configuration at: {path}",
        "config_use_existing_question": "Do you want to use the existing configuration?",
        "config_not_found_setup": "🔧 No configuration found. Let's set it up!",
        "config_invalid_360_id": "❌ Yandex 360 organization ID should be numeric (e.g., 8015133)",
        "config_invalid_cloud_id": "❌ Cloud organization ID should be alphanumeric string (e.g., bpfstkj3gi1dfd2s5d4d)",
        "audit_config_required": "❌ Configuration required. Run 'configure' command first.",
        "audit_init_failed": "❌ Failed to initialize auditor: {error}",
        "audit_no_queues": "❌ No queues found or failed to fetch queues.",
        "audit_export_failed": "⚠️  Audit completed but export failed.",
        "audit_cancelled": "❌ Audit cancelled by user.",
        "audit_failed": "❌ Audit failed: {error}",
        "goodbye": "👋 Goodbye!",
        
        # Audit process messages
        "fetching_all_queues": "🔍 Fetching all queues...",
        "auditing_access_permissions": "🔐 Auditing queue access permissions...",
        "audited_summary": "✅ Audited {queues} queues, found {entries} access entries",
        "no_queue_data": "❌ No queue data available",
        "more_queues": "... and {count} more queues",
        
        # Table columns
        "col_queue_key": "Queue Key",
        "col_name": "Name", 
        "col_lead": "Lead",
        "col_access_entries": "Access Entries",
        "auditing_queues": "Auditing queues...",
        
        # Export messages
        "exporting_to_excel": "📊 Exporting audit results to Excel...",
        "export_success": "✅ Audit results exported to: {path}",
        "export_error": "❌ Error exporting to Excel: {error}",
        
        # Additional audit messages
        "audit_starting": "🔍 Starting comprehensive audit of Yandex Tracker",
        "audit_started_title": "Audit Started",
        "audit_completed_success": "✅ Audit completed successfully!",
        "audit_results_exported": "📊 Results exported to: [bold]{path}[/bold]",
        "audit_total_queues": "📈 Total queues audited: [bold]{count}[/bold]",
        "audit_total_entries": "🔐 Total access entries: [bold]{count}[/bold]",
        "audit_complete_title": "🎉 Audit Complete",
        
        # Missing keys from audit.py
        "loading_queues": "Loading queues...",
        "found_queues": "Found {count} queues",
        "loaded_queues": "✅ Loaded {count} queues",
        "queues_loaded": "✅ Successfully loaded {count} queues",
        "queue_summary": "📊 Queue Summary",
        "access_summary": "📈 Access Summary",
        "total_access_entries": "  • Total access entries: {count}",
        "subject_type_count": "  • {type}: {count} entries",
        
        # Command help texts
        "configure_reset_help": "Reset existing configuration",
        "audit_output_help": "Output Excel file path",
        "audit_summary_help": "Show summary after audit",
        "audit_scope_help": "Audit scope: groups, users, both, or all_users_group",
        
        # Audit scope selection
        "audit_scope_selection_title": "🎯 Audit Scope Selection",
        "audit_scope_selection_description": """Choose what to audit for better performance:

[bold]Groups Only[/bold]: Fast - Only check group permissions
[bold]Users Only[/bold]: Slow - Check individual user permissions  
[bold]Both[/bold]: Comprehensive but slowest - Check both groups and users""",
        "audit_scope_groups_only": "Groups Only (Fast)",
        "audit_scope_users_only": "Users Only (Slow)", 
        "audit_scope_both": "Both Groups and Users (Comprehensive)",
        "audit_scope_all_users_group": "Queues with All Users Group Access (Very Fast)",
        "audit_scope_warning": "Note: User permissions audit can take significantly longer for large organizations",
        "audit_scope_select": "Select audit scope",
        
        # Access Issues
        "access_issues_title": "Queues with Access Issues",
        "access_issues_queue_key": "Queue Key",
        "access_issues_queue_name": "Queue Name",
        "access_issues_owner": "Owner",
        "access_issues_email": "Contact Email",
        "access_issues_status": "Status",
        "access_issues_deleted": "Deleted",
        "access_issues_active": "Active",
        "access_issues_contact_note": "Contact the queue owners above to request access for auditing these queues.",
        
        # API Error messages
        "api_error_unauthorized": "❌ Unauthorized: Check your OAuth token",
        "api_error_forbidden": "❌ Forbidden: Insufficient permissions",
        "api_error_rate_limit": "❌ Rate limit exceeded: Too many requests",
        "api_error_server": "❌ Server error {code}: Please try again later",
        "api_error_timeout": "❌ Request timeout: API is not responding",
        "api_error_connection": "❌ Connection error: Unable to connect to API",
    },
    
    "ru": {
        # CLI Messages
        "app_help": "🔍 Инструмент аудита Yandex Tracker - Аудит очередей и прав доступа",
        "configure_help": "🔧 Настроить OAuth токен и ID организации.",
        "audit_help": "🔍 Провести аудит всех очередей и их прав доступа.",
        "info_help": "ℹ️  Показать информацию о текущей конфигурации и инструменте.",
        
        # Configuration
        "config_found": "✅ Найдена существующая конфигурация: {path}",
        "config_token": "   Токен: {token}",
        "config_org_id": "   ID организации: {org_id}",
        "config_use_existing": "Хотите использовать существующую конфигурацию?",
        "config_not_found": "🔧 Конфигурация не найдена. Давайте настроим!",
        "config_setup_title": "🔐 Требуется настройка",
        "config_setup_description": """[bold blue]Конфигурация API Yandex Tracker[/bold blue]

Для использования инструмента вам нужно:
1. [bold]OAuth токен[/bold]: Получите на https://oauth.yandex.com/
2. [bold]ID организации[/bold]: Найдите в настройках организации Tracker

[yellow]Примечание:[/yellow] Ваши учетные данные будут безопасно сохранены в ~/.tracker_audit/.env""",
        "config_enter_token": "[bold]Введите ваш OAuth токен[/bold]",
        "config_enter_org_id": "[bold]Введите ID организации[/bold]",
        "config_select_org_type": "[bold]Выберите тип организации[/bold]",
        "config_org_type_360": "Yandex 360 для бизнеса (числовой ID, например, 8015133)",
        "config_org_type_cloud": "Yandex Cloud Organization (строковый ID, например, bpfstkj3gi1dfd2s5d4d)",
        "config_select_language": "[bold]Select language / Выберите язык[/bold]",
        "config_language_english": "English",
        "config_language_russian": "Русский",
        "config_invalid_token": "❌ Неверный токен. Пожалуйста, введите корректный OAuth токен.",
        "config_invalid_org_id": "❌ Неверный ID организации. Пожалуйста, введите корректный ID.",
        "config_testing": "🧪 Тестирование конфигурации...",
        "config_test_success": "✅ Тест конфигурации прошел успешно!",
        "config_saved": "✅ Конфигурация сохранена в: {path}",
        "config_test_failed": "❌ Тест конфигурации не удался: {error}",
        "config_check_credentials": "Пожалуйста, проверьте ваш токен и ID организации.",
        "config_try_again": "Хотите попробовать снова?",
        "config_completed": "🎉 Конфигурация завершена успешно!",
        "config_failed": "❌ Настройка не удалась.",
        "config_required": "❌ Требуется конфигурация. Сначала выполните команду 'configure'.",
        "config_current": "✅ Текущая конфигурация:",
        "config_file_location": "   Файл конфигурации: {path}",
        
        # Audit Process
        "audit_started": "🔍 Начинается комплексный аудит Yandex Tracker",
        "audit_title": "Аудит запущен",
        "fetching_queues": "🔍 Получение всех очередей...",
        "queues_loaded": "✅ Успешно загружено {count} очередей",
        "auditing_permissions": "🔐 Аудит прав доступа к очередям...",
        "auditing_queue": "  Аудит {queue}...",
        "auditing_queue_with_progress": "Аудит {queue} [{current}/{total}]",
        "audit_complete_summary": "✅ Проведен аудит {queues} очередей, найдено {entries} записей доступа",
        "no_queues_found": "❌ Очереди не найдены или не удалось их получить.",
        "audit_cancelled": "❌ Аудит отменен пользователем.",
        "audit_failed": "❌ Аудит не удался: {error}",
        "audit_failed_export": "⚠️  Аудит завершен, но экспорт не удался.",
        
        # Export
        "exporting_excel": "📊 Экспорт результатов аудита в Excel...",
        "export_success": "✅ Результаты аудита экспортированы в: {path}",
        "export_failed": "❌ Ошибка экспорта в Excel: {error}",
        
        # Results
        "queue_summary": "📊 Сводка по очередям",
        "access_summary": "📈 Сводка по доступу:",
        "total_access_entries": "  • Всего записей доступа: {count}",
        "subject_type_count": "  • {type}: {count} записей",
        "audit_complete_title": "🎉 Аудит завершен",
        "audit_results": """✅ Аудит завершен успешно!

📊 Результаты экспортированы в: [bold]{path}[/bold]
📈 Всего очередей проверено: [bold]{queues}[/bold]
🔐 Всего записей доступа: [bold]{entries}[/bold]""",
        
        # Info
        "tool_info_title": "📋 Информация об инструменте",
        "tool_info_description": """[bold blue]Инструмент аудита Yandex Tracker[/bold blue]

[bold]Назначение:[/bold]
Этот инструмент проводит аудит очередей Yandex Tracker и их прав доступа,
предоставляя подробные отчеты в формате Excel.

[bold]Возможности:[/bold]
• 🔍 Аудит всех очередей в вашей организации
• 🔐 Проверка прав доступа и назначений пользователей
• 📊 Экспорт подробных результатов в Excel

[bold]Команды:[/bold]
• [cyan]configure[/cyan] - Настроить OAuth токен и ID организации
• [cyan]audit[/cyan] - Запустить комплексный аудит
• [cyan]info[/cyan] - Показать эту информацию""",
        "config_ready": "✅ Конфигурация: Готова",
        "config_not_setup": "⚠️  Конфигурация: Не настроена",
        "config_get_started": "Выполните команду [bold cyan]configure[/bold cyan] для начала работы",
        "goodbye": "👋 До свидания!",
        
        # Table Headers
        "queue_key": "Ключ очереди",
        "name": "Название",
        "lead": "Ответственный",
        "access_entries": "Записи доступа",
        "description": "Описание",
        "default_type": "Тип по умолчанию",
        "default_priority": "Приоритет по умолчанию",
        
        # Progress Messages
        "loading_queues": "Загрузка очередей...",
        "found_queues": "Найдено {count} очередей",
        "loaded_queues": "✅ Загружено {count} очередей",
        
        # Error Messages
        "error_fetching_queues": "❌ Ошибка получения очередей: {error}",
        "error_initializing_auditor": "❌ Не удалось инициализировать аудитор: {error}",
        "could_not_get_users": "Не удалось получить пользователей: {error}",
        "could_not_get_groups": "Не удалось получить группы: {error}",
        "could_not_get_permissions": "Не удалось получить права для {type} {id} в очереди {queue}: {error}",
        "could_not_audit_queue": "Не удалось провести аудит прав для очереди {queue}: {error}",
        
        # Additional untranslated strings
        "config_found_existing": "✅ Найдена существующая конфигурация: {path}",
        "config_use_existing_question": "Хотите использовать существующую конфигурацию?",
        "config_not_found_setup": "🔧 Конфигурация не найдена. Давайте настроим!",
        "config_invalid_360_id": "❌ ID организации Yandex 360 должен быть числовым (например, 8015133)",
        "config_invalid_cloud_id": "❌ ID Cloud организации должен быть буквенно-цифровой строкой (например, bpfstkj3gi1dfd2s5d4d)",
        "audit_config_required": "❌ Требуется конфигурация. Сначала выполните команду 'configure'.",
        "audit_init_failed": "❌ Не удалось инициализировать аудитор: {error}",
        "audit_no_queues": "❌ Очереди не найдены или не удалось их получить.",
        "audit_export_failed": "⚠️  Аудит завершен, но экспорт не удался.",
        "audit_cancelled": "❌ Аудит отменен пользователем.",
        "audit_failed": "❌ Аудит не удался: {error}",
        "goodbye": "👋 До свидания!",
        
        # Audit process messages
        "fetching_all_queues": "🔍 Получение всех очередей...",
        "auditing_access_permissions": "🔐 Аудит прав доступа к очередям...",
        "audited_summary": "✅ Проведен аудит {queues} очередей, найдено {entries} записей доступа",
        "no_queue_data": "❌ Данные очередей недоступны",
        "more_queues": "... и еще {count} очередей",
        
        # Table columns
        "col_queue_key": "Ключ очереди",
        "col_name": "Название", 
        "col_lead": "Ответственный",
        "col_access_entries": "Записи доступа",
        "auditing_queues": "Аудит очередей...",
        
        # Export messages
        "exporting_to_excel": "📊 Экспорт результатов аудита в Excel...",
        "export_success": "✅ Результаты аудита экспортированы в: {path}",
        "export_error": "❌ Ошибка экспорта в Excel: {error}",
        
        # Additional audit messages
        "audit_starting": "🔍 Запуск комплексного аудита Yandex Tracker",
        "audit_started_title": "Аудит запущен",
        "audit_completed_success": "✅ Аудит завершен успешно!",
        "audit_results_exported": "📊 Результаты экспортированы в: [bold]{path}[/bold]",
        "audit_total_queues": "📈 Всего проверено очередей: [bold]{count}[/bold]",
        "audit_total_entries": "🔐 Всего записей доступа: [bold]{count}[/bold]",
        "audit_complete_title": "🎉 Аудит завершен",
        
        # Missing keys from audit.py
        "loading_queues": "Загрузка очередей...",
        "found_queues": "Найдено очередей: {count}",
        "loaded_queues": "✅ Загружено очередей: {count}",
        "queues_loaded": "✅ Успешно загружено очередей: {count}",
        "queue_summary": "📊 Сводка очередей",
        "access_summary": "📈 Сводка доступа",
        "total_access_entries": "  • Всего записей доступа: {count}",
        "subject_type_count": "  • {type}: {count} записей",
        
        # Command help texts
        "configure_reset_help": "Сбросить существующую конфигурацию",
        "audit_output_help": "Путь к выходному Excel файлу",
        "audit_summary_help": "Показать сводку после аудита",
        "audit_scope_help": "Область аудита: группы, пользователи, оба или группа всех пользователей",
        
        # Audit scope selection
        "audit_scope_selection_title": "🎯 Выбор области аудита",
        "audit_scope_selection_description": """Выберите что проверять для лучшей производительности:

[bold]Только группы[/bold]: Быстро - Проверка только прав групп
[bold]Только пользователи[/bold]: Медленно - Проверка индивидуальных прав пользователей  
[bold]Группы и пользователи[/bold]: Полный аудит, но самый медленный""",
        "audit_scope_groups_only": "Только группы (Быстро)",
        "audit_scope_users_only": "Только пользователи (Медленно)", 
        "audit_scope_both": "Группы и пользователи (Полный аудит)",
        "audit_scope_all_users_group": "Очереди с доступом группы 'Все пользователи' (Очень быстро)",
        "audit_scope_warning": "Примечание: Аудит прав пользователей может занять значительно больше времени для крупных организаций",
        "audit_scope_select": "Выберите область аудита",
        
        # Access Issues
        "access_issues_title": "Очереди с проблемами доступа",
        "access_issues_queue_key": "Ключ очереди",
        "access_issues_queue_name": "Название очереди",
        "access_issues_owner": "Владелец",
        "access_issues_email": "Email для связи",
        "access_issues_status": "Статус",
        "access_issues_deleted": "Удалена",
        "access_issues_active": "Активна",
        "access_issues_contact_note": "Обратитесь к владельцам очередей выше для запроса доступа к аудиту этих очередей.",
        
        # API Error messages
        "api_error_unauthorized": "❌ Не авторизован: Проверьте OAuth токен",
        "api_error_forbidden": "❌ Доступ запрещен: Недостаточно прав",
        "api_error_rate_limit": "❌ Превышен лимит запросов: Слишком много запросов",
        "api_error_server": "❌ Ошибка сервера {code}: Попробуйте позже",
        "api_error_timeout": "❌ Таймаут запроса: API не отвечает",
        "api_error_connection": "❌ Ошибка соединения: Не удается подключиться к API",
    }
}


# Global translator instance
_translator = Translator()

def get_translator() -> Translator:
    """Get the global translator instance."""
    return _translator

def t(key: str, **kwargs) -> str:
    """Shortcut function for translation."""
    return _translator.t(key, **kwargs)
