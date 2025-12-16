import argparse

from src.client.NoobCashClient import NoobCashClient

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--ip", help="IP of the host", default="127.0.0.1")
    args = argParser.parse_args()

    client = NoobCashClient(args.ip)
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")