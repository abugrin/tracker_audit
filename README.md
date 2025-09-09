# Yandex Tracker Audit Tool

A modern Python CLI tool for auditing Yandex Tracker queues and access permissions with beautiful output and Excel export capabilities.

**[Русская версия документации](README_RU.md)**

## Installation

1. **Clone or create the project directory**:
   ```bash
   mkdir tracker_audit && cd tracker_audit
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before using the tool, you need to configure your Yandex Tracker credentials:

1. **Get OAuth Token**:
   - Visit https://yandex.ru/support/tracker/ru/concepts/access
   - Create a new application or use existing one
   - Get your OAuth token

2. **Find Organization ID**:
   - Go to your Yandex Tracker organization settings
   - Find your Organization ID

3. **Configure the tool**:
   ```bash
   python main.py configure
   ```

The tool will guide you through the setup process and securely store your credentials.

## Usage

### Basic Commands

```bash
# Configure credentials (first time setup)
python main.py configure

# Run comprehensive audit
python main.py audit

# Run audit with custom output file
python main.py audit --output my_audit_report.xlsx

# Show tool information
python main.py info

# Get help
python main.py --help
```

### Advanced Usage

```bash
# Reset configuration
python main.py configure --reset

# Run audit without summary
python main.py audit --no-summary

# Run audit with specific output path
python main.py audit -o /path/to/reports/audit_$(date +%Y%m%d).xlsx

# Audit scope options for better performance
python main.py audit --scope groups        # Fast: Groups only
python main.py audit --scope users         # Slow: Users only  
python main.py audit --scope both          # Complete: Both (default)
```

### Audit Scope Options

The tool offers three audit scope options to balance speed and completeness:

- **Groups Only** (`--scope groups`): Fast audit checking only group permissions
- **Users Only** (`--scope users`): Slower audit checking individual user permissions
- **Both** (`--scope both`): Complete audit checking both groups and users (default)

⚠️ **Note**: User permissions audit can take significantly longer for large organizations due to API rate limits.

## Output

The tool generates an Excel file with three sheets:

1. **Summary**: Overview statistics and breakdowns
2. **Queues**: Detailed information about all queues
3. **Access Permissions**: Complete access audit with permissions details

## Project Structure

```
tracker_audit/
├── main.py           # Main CLI application
├── config.py         # Configuration management
├── audit.py          # Audit functionality
├── export.py         # Excel export functionality
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── venv/            # Virtual environment (created during setup)
```

## Requirements

- Python 3.8+
- Yandex Tracker access with appropriate permissions
- OAuth token for API access

## Dependencies

- `yandex_tracker_client` - Official Yandex Tracker API client
- `typer` - Modern CLI framework
- `rich` - Beautiful terminal formatting
- `openpyxl` - Excel file generation
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## Security

- OAuth tokens are stored securely in `~/.tracker_audit/.env`
- Tokens are never displayed in full in the CLI
- Configuration files are created with appropriate permissions

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Verify your OAuth token is correct
   - Check your organization ID
   - Ensure your token has necessary permissions

2. **Permission Denied**:
   - Make sure your account has access to view queue permissions
   - Contact your Tracker administrator for necessary permissions

3. **No Queues Found**:
   - Verify you have access to queues in your organization
   - Check if your organization ID is correct

### Getting Help

Run `python main.py --help` for detailed command information or `python main.py info` for tool overview.

## License

This project is provided as-is for auditing Yandex Tracker installations.
