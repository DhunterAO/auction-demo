from typing import Optional, List

from algosdk.v2client.algod import AlgodClient
from algosdk.kmd import KMDClient
import json

from ..account import Account

with open("../testnet/Primary/config.json","r") as fin:
    config = json.load(fin)

config['EnableDeveloperAPI'] = True

with open("../testnet/Primary/config.json","w") as fout:
    json.dump(config, fout)

with open("../testnet/Primary/algod.net","r") as fin:
    ALGOD_ADDRESS = "http://" + fin.read().strip()

with open("../testnet/Primary/algod.token","r") as fin:
    ALGOD_TOKEN = fin.read().strip()

def getAlgodClient() -> AlgodClient:
    return AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


with open("../testnet/Primary/kmd-v0.5/kmd.net","r") as fin:
    KMD_ADDRESS = "http://" + fin.read().strip()

with open("../testnet/Primary/kmd-v0.5/kmd.token","r") as fin:
    KMD_TOKEN = fin.read().strip()


def getKmdClient() -> KMDClient:
    return KMDClient(KMD_TOKEN, KMD_ADDRESS)


KMD_WALLET_NAME = "unencrypted-default-wallet"
KMD_WALLET_PASSWORD = ""

kmdAccounts: Optional[List[Account]] = None


def getGenesisAccounts() -> List[Account]:
    global kmdAccounts

    if kmdAccounts is None:
        kmd = getKmdClient()

        wallets = kmd.list_wallets()
        walletID = None
        for wallet in wallets:
            if wallet["name"] == KMD_WALLET_NAME:
                walletID = wallet["id"]
                break

        if walletID is None:
            raise Exception("Wallet not found: {}".format(KMD_WALLET_NAME))

        walletHandle = kmd.init_wallet_handle(walletID, KMD_WALLET_PASSWORD)

        try:
            addresses = kmd.list_keys(walletHandle)
            privateKeys = [
                kmd.export_key(walletHandle, KMD_WALLET_PASSWORD, addr)
                for addr in addresses
            ]
            kmdAccounts = [Account(sk) for sk in privateKeys]
        finally:
            kmd.release_wallet_handle(walletHandle)

    return kmdAccounts