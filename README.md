# V-Liquifier Python Script

<b style='color:red'>WARNING: This script is a work in progress and is not ready for any production or test environments</b>


## Overview

This Python script interacts with the Lightning Network using the `lncli` command-line tool to:

- List invoices within a user-defined date range.
- Calculate and display total payment amounts for settled invoices.
- Determine the number of payments needed and the amount of each payout.
- List eligible channels for making these payouts.

## Setup

1. Clone the repository:
    ```bash
    git clone <URL-of-this-repo>
    ```
2. Set up a Python virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
4. Copy the `.env.sample` file to `.env` and fill it with your details:
    ```bash
    cp .env.sample .env
    ```
    Then edit the `.env` file and provide the following variables:
    - `TLS_CERT_PATH`: Path to your tls certificate.
    - `MACAROON_PATH`: Path to your macaroon file.
    - `MAXIMUM_PAYMENT_AMOUNT`: Maximum payment amount in satoshis.

## Usage

Run the script by using the following command:
```bash
python3 v-liquifier.py
```

During execution, the script will prompt you to enter a start and end date for invoice listing. Enter the dates in the format `YYYY-MM-DD`.

## Output

The script will display a table of invoices with their creation date, amount paid, R Hash, and state. It will also show the total amount paid for settled invoices and the number of payments needed to settle them. Finally, it will list all eligible channels that can be used for payments, displaying their ID, capacity, local balance, active status, and local balance ratio.

Please note that this script does not make any actual payments or modifications to your Lightning Network channels currently. It is a tool for analysis and planning.

