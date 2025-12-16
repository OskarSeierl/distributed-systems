from Crypto.PublicKey import RSA


class Wallet:

    def __init__(self):
        """
        Initialize a new wallet.
        Generates a new RSA key pair (private and public key).
        Sets the address as the exported public key.
        Initializes an empty list of transactions.
	    """
        key = RSA.generate(2048)

        self.private_key = key                              # Private key
        self.public_key = key.publickey()                   # Public key
        self.address = key.publickey().exportKey().decode() # Wallet address (public key in string format)
        self.transactions = []                              # List of transactions associated with this wallet