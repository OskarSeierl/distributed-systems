import json

import Crypto
import Crypto.Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from src.utils.logger import Logger


class Transaction:

    def __init__(self, sender_address, sender_private_key, receiver_address, value):
        """
        Initialize a new transaction.

        :param sender_address: The public key of the wallet sending the money.
        :param sender_private_key: The private key of the sender (unused in init).
        :param receiver_address: The public key of the wallet receiving the money.
        :param value: The amount to be transferred.
        """
        self.sender_address = sender_address        # Sender's public key
        self.receiver_address = receiver_address    # Receiver's public key
        self.amount = value                         # Amount to transfer
        self.transaction_inputs = None              # List of Transaction Inputs
        self.transaction_outputs = None             # List of Transaction Outputs
        self.signature = None                       # Signature of the transaction
        self.transaction_id = self.calculate_hash() # Transaction hash

    def calculate_hash(self):
        """
        Calculate hash of transaction and use it as its ID.

        :return: The calculated transaction ID (hash).
        """
        self.transaction_id = Crypto.Random.get_random_bytes(128).decode("ISO-8859-1")
        return self.transaction_id

    def to_dict(self):
        """
        Convert transaction object to dictionary for readability.

        :return: A dictionary representation of the transaction.
        """
        data = {
            "sender_address": self.sender_address,
            "receiver_address": self.receiver_address,
            "amount": self.amount,
            "transaction_id": self.transaction_id,
            "transaction_inputs": self.transaction_inputs,
            "transaction_outputs": self.transaction_outputs,
            "signature": self.signature
        }
        return data


    def get_sign_payload(self):
        """
        Prepare the payload for signing the transaction.
        """
        return json.dumps({
            "sender": str(self.sender_address),
            "receiver": str(self.receiver_address),
            "amount": float(self.amount),
            "id": str(self.transaction_id)
        }, sort_keys=True)  # sort_keys is vital for consistent hashing

    def sign_transaction(self, private_key):
        """
        Sign the transaction with the sender's private key.

        :param private_key: The RSA private key of the sender.
        """
        payload = self.get_sign_payload()
        h = SHA256.new(payload.encode('utf-8'))
        signer = PKCS1_v1_5.new(private_key)
        self.signature = signer.sign(h)

    def verify_signature(self):
        """
        Verify the transaction signature using the sender's public key.
        """
        if not self.signature:
            return False
        try:
            payload = self.get_sign_payload()
            h = SHA256.new(payload.encode('utf-8'))
            public_key = RSA.importKey(self.sender_address)
            verifier = PKCS1_v1_5.new(public_key)

            # In PKCS1_v1_5, verify() raises an exception if invalid
            verifier.verify(h, self.signature)
            return True
        except (ValueError, TypeError):
            return False

    def validate_transaction(self, utxo_id, utxos):
        """
        Verify signature of sender and verify sender has enough amount to spend.

        :param utxo_id: The identifier (address) to check in UTXOs.
        :param utxos: The dictionary of Unspent Transaction Outputs.
        :return: True if transaction is valid, False otherwise.
        """
        balance = 0
        for utxo in utxos[utxo_id]:
            balance += utxo.amount
        if not self.verify_signature():
            Logger.error("Transaction NOT Validated: Not valid address")
            return False
        elif balance < self.amount:
            Logger.error("Transaction NOT Validated: Not enough coins")
            return False
        else:
            Logger.success("Transaction Validated !")
            return True