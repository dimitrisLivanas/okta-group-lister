# Okta Group Lister CLI

A command-line tool to list groups in your Okta organization in a convenient, formatted table.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dimitrisLivanas/okta-group-lister.git
    cd okta-group-lister
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```
3.  **Install the required dependencies:**
    ```bash
    pip install requests tabulate
    ```
    This command will install the necessary libraries.

## Usage

1.  **Set the `OKTA_DOMAIN` and `OKTA_API_TOKEN` environment variables.**
    * **macOS/Linux:**
        ```bash
        export OKTA_DOMAIN="your-okta-domain.com"
        export OKTA_API_TOKEN="your-api-token"
        ```
    * **Windows (Command Prompt):**
        ```bash
        set OKTA_DOMAIN=your-okta-domain.com
        set OKTA_API_TOKEN=your-api-token
        ```
    * **Windows (PowerShell):**
        ```powershell
        $env:OKTA_DOMAIN = "your-okta-domain.com"
        $env:OKTA_API_TOKEN = "your-api-token"
        ```
2.  **Run the script:**
    ```bash
    python okta_group_lister.py
    ```
    This will fetch and display your Okta groups in a formatted table.

## Dependencies

This project requires the `requests` and `tabulate` Python libraries. You can install them using `pip`.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Push your changes to your fork.
5.  Submit a pull request.

Please ensure your code adheres to any existing style guidelines and includes appropriate tests.

## Authors

* Dimitris Livanas/dimitrisLivanas
