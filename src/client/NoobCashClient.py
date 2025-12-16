import os

import questionary
import requests
from texttable import Texttable

from src.client.MenuOption import MenuOption

HELP_MAP = {
    MenuOption.NEW_TRANSACTION: "Initialize a new transfer of NoobCoins to another node.\n   Requires: Recipient ID and Amount.",
    MenuOption.VIEW_TRANSACTIONS: "Fetch and display the transactions contained in the last validated block.",
    MenuOption.SHOW_BALANCE: "Display the current wallet balance of this client.",
    MenuOption.CONNECT: "Establish a connection to a specific node port (e.g., 8000).",
    MenuOption.DISCONNECT: "Close the session with the current node.",
    MenuOption.NETWORK_STATUS: "Scan local ports (8000-8009) to discover active nodes and check their status.",
    MenuOption.HELP: "Show this help message.",
    MenuOption.EXIT: "Close the application."
}

class NoobCashClient:
    def __init__(self, ip):
        """
        Initialize the NoobCash client.

        :param ip: The IP address of the host.
        """
        self.ip = ip
        self.port = None  # Currently connected port

    @property
    def is_connected(self):
        """
        Check if the client is connected to a node.

        :return: True if connected, False otherwise.
        """
        return self.port is not None

    def get_address(self, port=None):
        """
        Returns the full URL for a given port (or current port if None).

        :param port: The port to connect to. If None, uses the current port.
        :return: The full URL string.
        """
        target_port = port if port else self.port
        return f"http://{self.ip}:{target_port}"

    def check_connection(self, port):
        """
        Pings a node to verify it is active.

        :param port: The port to check.
        :return: True if the node is active, False otherwise.
        """
        try:
            url = f"{self.get_address(port)}/api/get_balance"
            requests.get(url, timeout=2)
            return True
        except requests.exceptions.RequestException:
            return False

    def clear_screen(self):
        """
        Clears the terminal screen.
        """
        # Cross-platform clear
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self):
        """
        Pauses execution until the user presses a key.
        """
        # Helper to pause execution
        questionary.press_any_key_to_continue().ask()
        self.clear_screen()

    def handle_new_transaction(self):
        """
        Handles the creation of a new transaction.
        Prompts the user for recipient ID and amount, then sends the request.
        """
        # Sequential questions using Questionary
        recipient = questionary.text("🍀 What is the Recipient ID?").ask()
        if recipient is None: return  # User cancelled

        amount = questionary.text("🪙 How many NoobCoins to send?").ask()
        if amount is None: return  # User cancelled

        print(f"Sending {amount} NoobCoins to client {recipient}...")
        try:
            url = f"{self.get_address()}/api/create_transaction/{recipient}/{amount}"
            response = requests.get(url)
            print(f"Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Transaction failed: {e}")

    def handle_view_transactions(self):
        """
        Fetches and displays the transactions in the last validated block.
        """
        try:
            url = f"{self.get_address()}/api/view_transactions"
            response = requests.get(url)
            data = response.json()

            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.set_cols_align(["c", "c", "c"])
            rows = [["Sender", "Receiver", "Amount"]]

            for line in data:
                # Adjust keys here if your API returns different dict keys
                rows.append([line.get("sender_id"), line.get("receiver_id"), line.get("amount")])

            table.add_rows(rows)
            print(table.draw())
        except Exception as e:
            print(f"❌ Could not fetch transactions: {e}")

    def handle_show_balance(self):
        """
        Fetches and displays the current wallet balance.
        """
        try:
            url = f"{self.get_address()}/api/get_balance"
            response = requests.get(url)
            print(f"💰 Current Balance: {response.json()} NBC")
        except Exception as e:
            print(f"❌ Could not fetch balance: {e}")

    def handle_connect(self):
        """
        Handles the connection to a specific node port.
        Prompts the user for the port number.
        """
        port_str = questionary.text("Enter the node port").ask()

        if not port_str: return

        try:
            new_port = int(port_str)
            print(f"Connecting to {self.ip}:{new_port}...")

            if self.check_connection(new_port):
                self.port = new_port
                print(f"✅ Connected successfully to port {self.port}")
            else:
                print(f"❌ Connection failed: Node at port {new_port} is unreachable.")
        except ValueError:
            print("❌ Invalid port number.")

    def handle_network_status(self):
        """
        Scans the local network (ports 8000-8009) to discover active nodes and check their status.
        """
        print("📡 Scanning local network (ports 8000-8009)...")

        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "c", "c"])
        rows = [["Port", "Status", "Balance"]]

        for p in range(8000, 8010):
            status = "🔴 Offline"
            balance = "N/A"

            if self.check_connection(p):
                status = "🟢 Online"
                try:
                    url = f"{self.get_address(p)}/api/get_balance"
                    res = requests.get(url, timeout=0.5)
                    balance = str(res.json())
                except:
                    pass

            rows.append([str(p), status, balance])

        table.add_rows(rows)
        print(table.draw())

    def handle_help(self, choices):
        """
        Displays the help message for the available menu options.

        :param choices: A list of available MenuOption choices.
        """
        self.clear_screen()
        print("📘 NOOBCASH CLIENT HELP\n" + "=" * 25)

        for choice in choices:
            description = HELP_MAP.get(choice, "No description available.")
            print(f"\n🔹 {choice.value}")
            print(f"   {description}")

        print("\n" + "=" * 25)

    def run(self):
        """
        Starts the main loop of the client application.
        """
        self.clear_screen()
        while True:
            # 1. Determine Choices
            if self.is_connected:
                print(f"🔌 Connected to Node at {self.ip}:{self.port}")
                choices = [
                    MenuOption.NEW_TRANSACTION,
                    MenuOption.VIEW_TRANSACTIONS,
                    MenuOption.SHOW_BALANCE,
                    MenuOption.DISCONNECT,
                    MenuOption.HELP,
                    MenuOption.EXIT
                ]
            else:
                print("🔌 Not connected to any node")
                choices = [
                    MenuOption.CONNECT,
                    MenuOption.NETWORK_STATUS,
                    MenuOption.HELP,
                    MenuOption.EXIT
                ]

            # 2. Render Menu using Questionary
            # qestionary.select returns the value selected directly
            choice_val = questionary.select(
                "Noobcash Client",
                choices=[c.value for c in choices]
            ).ask()

            if choice_val is None:
                # This catches Ctrl+C
                print("\nGoodbye!")
                break

            self.clear_screen()

            # 3. Dispatch
            if choice_val == MenuOption.NEW_TRANSACTION.value:
                self.handle_new_transaction()
                self.pause()

            elif choice_val == MenuOption.VIEW_TRANSACTIONS.value:
                self.handle_view_transactions()
                self.pause()

            elif choice_val == MenuOption.SHOW_BALANCE.value:
                self.handle_show_balance()
                self.pause()

            elif choice_val == MenuOption.CONNECT.value:
                self.handle_connect()
                self.pause()

            elif choice_val == MenuOption.DISCONNECT.value:
                self.port = None
                self.clear_screen()

            elif choice_val == MenuOption.NETWORK_STATUS.value:
                self.handle_network_status()
                self.pause()

            elif choice_val == MenuOption.HELP.value:
                self.handle_help(choices)
                self.pause()

            elif choice_val == MenuOption.EXIT.value:
                self.clear_screen()
                break
