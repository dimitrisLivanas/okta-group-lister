# Okta Group Lister

A command-line tool for listing and managing Okta groups and their members. This tool provides functionality to search for groups, list group members, and export member information in various formats.

## Features

- Search for Okta groups by name
- List members of specific groups
- Export group members to CSV, JSON, or Excel format
- Colorized output for better readability
- Pagination support for large groups
- Rate limiting handling
- Comprehensive error handling and logging

## Installation

### Option 1: Direct Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/okta-group-lister.git
    cd okta-group-lister
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Option 2: Using Docker

1. Build the Docker image:
    ```bash
    docker build -t okta-group-lister .
    ```

2. Run the container:
    ```bash
    docker run -it --rm \
        -e OKTA_DOMAIN=your-okta-domain \
        -e OKTA_API_TOKEN=your-okta-api-token \
        -v $HOME:/home/user \
        okta-group-lister [options]
    ```

## Configuration

Set up your Okta API credentials as environment variables:

```bash
export OKTA_DOMAIN="your-okta-domain"
export OKTA_API_TOKEN="your-okta-api-token"
```

## Usage

### List All Groups
```bash
python okta_group_lister.py
```

### Search for Groups
```bash
python okta_group_lister.py --search "group-name"
```

### List Group Members
```bash
python okta_group_lister.py --members "group-name-or-id"
```

### Export Group Members
```bash
# Export to CSV (default)
python okta_group_lister.py --export "group-name-or-id"

# Export to JSON
python okta_group_lister.py --export "group-name-or-id" --format json

# Export to Excel
python okta_group_lister.py --export "group-name-or-id" --format excel
```

### Enable Verbose Output
```bash
python okta_group_lister.py --verbose
```

## Output Formats

The tool supports three export formats:
- CSV (default): Comma-separated values
- JSON: JavaScript Object Notation
- Excel: Microsoft Excel spreadsheet

## Logging

The tool creates a log file in the current directory with the format `okta_group_lister_YYYYMMDD.log`. This file contains detailed information about API calls, errors, and other important events.

## Error Handling

The tool includes comprehensive error handling for:
- API errors
- Rate limiting
- Network issues
- Invalid responses
- File system errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
