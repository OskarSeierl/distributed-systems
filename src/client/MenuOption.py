from enum import Enum


class MenuOption(str, Enum):
    NEW_TRANSACTION = '💸 New transaction'
    VIEW_TRANSACTIONS = '📭 View last transactions'
    SHOW_BALANCE = '💰 Show balance'
    CONNECT = '🔌 Connect to Node'
    DISCONNECT = '🔌 Disconnect'
    NETWORK_STATUS = '🕸️ Network Status'
    HELP = '💁 Help'
    EXIT = '🌙 Exit'