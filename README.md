# Okta Group Lister CLI

A command-line tool to list and manage groups and their members in your Okta organization.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
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

    * **List all groups:**

        ```bash
        python3 okta_group_lister.py
        ```

        Displays a table of all groups in your Okta organization.

    * **Search for groups by name:**

        ```bash
        python3 okta_group_lister.py --search "search_term"
        ```

        Displays groups whose names contain the specified `"search_term"` (case-insensitive). For example:

        ```bash
        python3 okta_group_lister.py --search "team"
        ```

    * **List members of a group:**

        ```bash
        python3 okta_group_lister.py --members "group_name_or_id"
        ```

        Displays the members of a group. Specify the `"group_name_or_id"` either by its name or ID. If multiple groups share the same name, you **must** use the Group ID. For example:

        ```bash
        python3 okta_group_lister.py --members "My Group"
        python3 okta_group_lister.py --members "00g1a2b3c4d5Efg6h7i8"  # Replace with actual Group ID
        ```

    * **Export group members to a CSV file:**

        ```bash
        python3 okta_group_lister.py --export "group_name_or_id"
        ```

        Exports the members of a group to a CSV file in your home directory. Specify the `"group_name_or_id"` either by its name or ID. If multiple groups share the same name, you **must** use the Group ID. The file will be saved as `GROUP_NAME_members.csv` (where `GROUP_NAME` is the sanitized group name). For example:

        ```bash
        python3 okta_group_lister.py --export "My Group"
        python3 okta_group_lister.py --export "00g1a2b3c4d5Efg6h7i8"  # Replace with actual Group ID
        ```

## Dependencies

* Python 3.x
* `requests`
* `tabulate`

    Install the required packages using pip:

    ```bash
    pip install requests tabulate
    ```

## Contributing

Contributions are welcome!

1.  Fork the repository.
2.  Create a new branch.
3.  Make your changes and commit them.
4.  Push your changes to your fork.
5.  Submit a pull request.

## License

[Specify your license here, e.g., e.g., MIT License]

## Author

* Dimitris Livanas / dimitrisLivanas
