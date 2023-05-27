import csv
from tabulate import tabulate
import subprocess
import os
import json
from dotenv import load_dotenv
import datetime
import time
import logging

# Configure logging
logging.basicConfig(filename='log-v-liquifier.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get environment variables for lncli
tls_cert_path = os.environ['TLS_CERT_PATH']
macaroon_path = os.environ['MACAROON_PATH']

#Get environment variables to configure payments
maximum_payment_amount = int(os.environ['MAXIMUM_PAYMENT_AMOUNT'])

# Define a function to run lncli commands


def run_lncli_command(command, command_args=[]):
    # Build the command line arguments
    args = [
        'lncli',
        '--macaroonpath', macaroon_path,
        '--tlscertpath', tls_cert_path,
        command
    ] + command_args

    # Run the command and capture the output
    command_output = subprocess.check_output(args)

    # Parse the output as JSON
    output_json = json.loads(command_output)

    # Return the output as a JSON object
    return output_json

def convert_to_unix_time(date_string):
    # Convert string to datetime object
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')

    # Convert datetime object to unix timestamp
    unix_time = int(time.mktime(date.timetuple()))

    return unix_time

def get_date_input(prompt):
    while True:
        date_string = input(prompt)
        try:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
            # If the date string is valid, we can return it
            return date_string
        except ValueError:
            print("Invalid date. Please enter a date in format YYYY-MM-DD.")

def main():
    # Ask the user for the start date and end date
    start_date_string = get_date_input("Enter the start date (YYYY-MM-DD): ")
    end_date_string = get_date_input("Enter the end date (YYYY-MM-DD): ")

    # Convert the dates to unix time
    start_date_unix = convert_to_unix_time(start_date_string)
    end_date_unix = convert_to_unix_time(end_date_string)

    # Get the list of invoices between the user specified date range
    list_invoices_output = run_lncli_command('listinvoices', [f'--creation_date_start={start_date_unix}', f'--creation_date_end={end_date_unix}'])

    # Extract the relevant information and create a list of lists
    invoices_data = [[datetime.datetime.fromtimestamp(int(inv.get('creation_date', 0))).strftime('%Y-%m-%d %H:%M:%S'), int(inv.get('amt_paid_sat', 0)), inv.get('r_hash', 'N/A'), inv.get('state', 'N/A')] for inv in list_invoices_output.get('invoices', [])]

    # Print the data in a tabular format
    print(tabulate([[i[0], '{:,}'.format(i[1]), i[2], i[3]] for i in invoices_data], headers=['Creation Date', 'Amount Paid (Sat)', 'R Hash', 'State']))

    # Sum 'amt_paid_sat' values for invoices that are 'SETTLED'
    total_amt_paid_sat = sum(int(inv[1]) for inv in invoices_data if inv[3] == 'SETTLED')

    # Print the total amount
    print("\nTotal Amount Paid (Sat) for 'SETTLED' invoices:", '{:,}'.format(total_amt_paid_sat))

    # Check if total_amt_paid_sat is less than maximum_payment_amount
    if total_amt_paid_sat <= maximum_payment_amount:
        num_payments = 1
        payout_amount = total_amt_paid_sat
    else:
        # Calculate number of payments needed
        num_payments = -(-total_amt_paid_sat // maximum_payment_amount)  # equivalent to ceiling division

        # Calculate the payment amount, rounding to the nearest integer
        payout_amount = round(total_amt_paid_sat / num_payments)

    # Print the results
    print(f"\nNumber of Payments Needed: {num_payments}")
    print(f"Each Payout Amount: {payout_amount:,} Sat")

    # Run the lncli listchannels command
    list_channels_output = run_lncli_command('listchannels')

    # List to store eligible channels
    eligible_channels = []

    for channel in list_channels_output['channels']:
        # Extract the channel ID, capacity, local balance, and active status
        chan_id = channel['chan_id']
        capacity = int(channel['capacity'])
        local_balance = int(channel['local_balance'])
        active = channel['active']

        # If local_balance is greater than or equal to the payout_amount, append it to eligible_channels
        if local_balance >= payout_amount and active:
            # Calculate the local_balance_ratio
            local_balance_ratio = local_balance / capacity
            channel['local_balance_ratio'] = local_balance_ratio
            eligible_channels.append(channel)

    # Sort eligible_channels by local_balance_ratio in descending order
    eligible_channels.sort(key=lambda x: x['local_balance_ratio'], reverse=True)

    # Print the details of the eligible channels
    for channel in eligible_channels:
        # Extract the channel ID, capacity, local balance, and active status
        chan_id = channel['chan_id']
        capacity = int(channel['capacity'])
        local_balance = int(channel['local_balance'])
        active = channel['active']
        local_balance_ratio = channel['local_balance_ratio']  # Extract the local_balance_ratio

        # Print the channel information
        print(f"\nEligible Channel ID: {chan_id}\nCapacity: {capacity:,}\nLocal Balance: {local_balance:,}\nActive Status: {active}\nLocal Balance Ratio: {local_balance_ratio}\n{'-'*50}")

if __name__ == '__main__':
    main()