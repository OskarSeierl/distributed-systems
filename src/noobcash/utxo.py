class UTXO:

    def __init__(self, sender, receiver, amount):
        """
        Initialize a new UTXO (Unspent Transaction Output)

        :param sender: The address of the sender
        :param receiver: The address of the receiver
        :param amount: The amount of currency transferred
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
