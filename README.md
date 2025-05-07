# Okta Group Lister CLI

A command-line tool to list groups in your Okta organization in a convenient, formatted table.

## Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/).

* **MAJOR (X.y.z):** Incompatible API changes.
* **MINOR (x.Y.z):** Adds functionality in a backwards compatible manner.
* **PATCH (x.y.Z):** Fixes bugs in a backwards compatible manner.

## Current Version: 0.1.0 (2025-05-07)

### Features

* Initial release with the ability to fetch and display Okta groups in a formatted table.
* Authentication via `OKTA_DOMAIN` and `OKTA_API_TOKEN` environment variables.

## Upcoming Features (Roadmap)

* **[ ]** Filtering groups by name or other criteria using command-line arguments.
* **[ ]** Handling pagination for organizations with a large number of groups.
* **[ ]** Displaying more details about each group (e.g., member count, group type).
* **[ ]** Configuration via a dedicated configuration file.
* **[ ]** More robust error handling and logging.
* **[ ]** Packaging as a proper installable CLI tool.

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
    pip install -r requirements.txt
    ```
    This command will install the dependencies listed in the `requirements.txt` file.

## Usage

1.  **Set the `OKTA_DOMAIN` and `OKTA_API_TOKEN` environment variables.**
    * **macOS/Linux:**
        ```bash
        export OKTA_DOMAIN="your-okta-domain.okta.com"
        export OKTA_API_TOKEN="your-api-token"
        ```
    * **Windows (Command Prompt):**
        ```bash
        set OKTA_DOMAIN=your-okta-domain.okta.com
        set OKTA_API_TOKEN=your-api-token
        ```
    * **Windows (PowerShell):**
        ```powershell
        $env:OKTA_DOMAIN = "your-okta-domain.okta.com"
        $env:OKTA_API_TOKEN = "your-api-token"
        ```
2.  **Run the script:**
    ```bash
    python okta_group_lister.py
    ```
    This will fetch and display your Okta groups in a formatted table.

## Dependencies

This project uses the following Python libraries, which are listed in the `requirements.txt` file:
