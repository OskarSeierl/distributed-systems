from flask import Flask, request, jsonify, make_response, Response, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from copy import deepcopy
import os
import argparse
import pickle
import time
import threading

from src.noobcash.node import Node
from src.noobcash.transaction import Transaction
from src.noobcash.utxo import UTXO
from src.utils.logger import Logger

# Bootstrap Helper
def check_full_ring(node: Node, total_nodes: int):
    """
    Checks if the ring is full and broadcasts the ring, blockchain, and initial NBC if so.

    :param node: The node instance.
    :param total_nodes: The total number of nodes expected in the network.
    """
    time.sleep(1)
    if len(node.ring) == total_nodes:
        node.broadcast_ring()
        node.broadcast_blockchain()
        node.broadcast_initial_nbc()

def create_genesis_block(node: Node, total_nbc: int):
    """
    Create the first block of the blockchain (GENESIS BLOCK).
    Accepts the node and total initial NBCs to credit.

    :param node: The node instance.
    :param total_nbc: The total amount of NoobCoins to be distributed.
    """
    gen_block = node.create_new_block()  # previous_hash autogenerates
    gen_block.nonce = 0

    first_transaction = Transaction(
        sender_address='0',
        sender_private_key=None,
        receiver_address=node.wallet.address,
        value=total_nbc
    )

    gen_block.transactions_list.append(first_transaction)
    gen_block.calculate_hash()

    node.blockchain.chain.append(gen_block)
    # Add first UTXO - keep existing indexing scheme
    node.blockchain.UTXOs[0].append(UTXO(-1, node.id, total_nbc))

    node.current_block = node.create_new_block()

def init_node(args):
    """
    Initialize Node object, environment and bootstrap logic.
    Returns (node, total_nodes, total_nbc, bootstrap_node, ip_address, port).

    :param args: Command line arguments.
    :return: A tuple containing the initialized node, total nodes, total NBC, bootstrap node info, IP address, and port.
    """

    total_nodes = args.total_nodes
    total_nbc = total_nodes * 100

    load_dotenv()
    node = Node(total_nodes)

    bootstrap_node = {
        'ip': os.getenv('API_IP'),
        'port': os.getenv('BOOTSTRAP_PORT')
    }

    ip_address = args.ip
    port = args.port

    node.ip = ip_address
    node.port = str(port)

    # See if node is Bootstrap node
    if ip_address == bootstrap_node["ip"] and str(port) == bootstrap_node["port"]:
        node.is_bootstrap = True

    # Register node to the cluster
    if node.is_bootstrap:
        node.id = 0
        Logger.info("I am bootstrap")
        node.add_node_to_ring(node.id, node.ip, node.port, node.wallet.address, total_nbc)
        create_genesis_block(node, total_nbc)
    else:
        node.unicast_node(bootstrap_node)

    return node, total_nodes, total_nbc, bootstrap_node, ip_address, port


# App Factory
def create_app(node: Node, total_nodes: int, total_nbc: int):
    """
    Create and return Flask app with routes bound to the provided node.

    :param node: The node instance.
    :param total_nodes: The total number of nodes in the network.
    :param total_nbc: The total amount of NoobCoins.
    :return: The Flask application instance.
    """
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.route("/api/create_transaction/<int:receiver_id>/<int:amount>", methods=['GET'])
    def create_transaction(receiver_id: int, amount: int):
        if receiver_id >= total_nodes:
            return make_response(jsonify({"message": 'Node ID does not exist'}), 400)

        receiver_address = list(node.ring.keys())[receiver_id]
        transaction = node.create_transaction(receiver_address, amount)
        node.add_transaction_to_pending(transaction)
        node.broadcast_transaction(transaction)
        return make_response(jsonify({'message': 'Successful Transaction !'}), 200)

    @app.route("/api/view_transactions", methods=['GET'])
    def view_transactions():
        if len(node.blockchain.chain) <= 1:
            return jsonify('There are no mined blocks at the moment !')

        latest_block = node.blockchain.chain[-1]
        transactions = []
        for transaction in latest_block.transactions_list:
            transactions.append({
                "sender_id": node.ring[transaction.sender_address]['id'],
                "receiver_id": node.ring[transaction.receiver_address]['id'],
                "amount": transaction.amount
            })

        return make_response(jsonify(transactions), 200)

    @app.route("/api/get_balance", methods=['GET'])
    def get_balance():
        balance = node.ring[node.wallet.address]['balance']
        return make_response(jsonify({'balance': balance}), 200)

    @app.route("/api/get_chain_length", methods=['GET'])
    def get_chain_length():
        chain_len = len(node.blockchain.chain)
        return make_response(jsonify({'chain_length': chain_len}), 200)

    @app.route("/api/get_chain", methods=['GET'])
    def get_chain():
        return Response(pickle.dumps(node.blockchain), mimetype='application/octet-stream')

    @app.route("/api/node_info", methods=['GET'])
    def get_node_info():
        return make_response(jsonify({
            'id': node.id,
            'ip': node.ip,
            'port': node.port,
            'address': node.wallet.address,
            'balance': node.ring[node.wallet.address]['balance'] if node.wallet.address in node.ring else 0
        }), 200)

    # INTERNAL ROUTES
    @app.route("/", methods=['GET'])
    def root():
        return render_template('index.html')

    @app.route("/get_ring", methods=['POST'])
    def get_ring():
        data = request.data
        node.ring = pickle.loads(data)
        Logger.success("Ring received successfully !")
        return make_response('OK', 200)

    @app.route("/get_blockchain", methods=['POST'])
    def get_blockchain():
        data = request.data
        node.blockchain = pickle.loads(data)
        node.temp_utxos = deepcopy(node.blockchain.UTXOs)
        Logger.success("Blockchain received successfully !")
        return make_response('OK', 200)

    @app.route("/get_transaction", methods=['POST'])
    def get_transaction():
        data = request.data
        new_transaction = pickle.loads(data)
        Logger.info("New transaction received successfully !")
        node.add_transaction_to_pending(new_transaction)
        return make_response('OK', 200)

    @app.route("/get_block", methods=['POST'])
    def get_block():
        data = request.data
        new_block = pickle.loads(data)
        Logger.info("New block received successfully !")

        with node.processing_block_lock:
            if new_block.validate_block(node.blockchain):
                with node.incoming_block_lock:
                    node.incoming_block = True
                Logger.mining("Block was mined by someone else")
                Logger.success("Adding it to the chain")
                node.add_block_to_chain(new_block)
                Logger.info(f"Blockchain length: {len(node.blockchain.chain)}")
            elif node.blockchain.chain[-1].previous_hash == new_block.previous_hash:
                Logger.warning("Rejected incoming block")
            else:
                Logger.warning(f"Incoming block previous_hash: {new_block.previous_hash}")
                Logger.info("BLOCKCHAIN")
                Logger.info(str([block.hash[:7] for block in node.blockchain.chain]))
                node.blockchain.resolve_conflict(node)
                Logger.error("Something went wrong with validation")

        return make_response('OK', 200)

    @app.route("/let_me_in", methods=['POST'])
    def let_me_in():
        ip = request.form.get('ip')
        port_form = request.form.get('port')
        address = request.form.get('address')
        id = len(node.ring)

        node.add_node_to_ring(id, ip, port_form, address, 0)

        t = threading.Thread(target=check_full_ring, args=(node, total_nodes))
        t.start()

        return make_response(jsonify({'id': id}), 200)

    return app

# Entrypoint
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
    parser.add_argument("--ip", help="IP of the host", default="127.0.0.1")
    parser.add_argument("--total_nodes", help="Total number of nodes in the network", default=5, type=int)

    args = parser.parse_args()

    node, total_nodes, total_nbc, bootstrap_node, ip_address, port = init_node(args)
    app = create_app(node, total_nodes, total_nbc)

    app.run(host=ip_address, port=port)


if __name__ == "__main__":
    main()
