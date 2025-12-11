from bittensor_wallet import Keypair
import json
from pathlib import Path


def load_keypair_from_file(hotkey_file_path: str) -> Keypair:
    """Load a Keypair from a bittensor key file"""
    hotkey_path = Path(hotkey_file_path)

    if not hotkey_path.exists():
        raise FileNotFoundError(f"Key file not found: {hotkey_file_path}")

    # Read the key file
    with open(hotkey_path, "r") as f:
        key_data = json.load(f)

    # Create Keypair from the private key
    private_key = key_data.get("privateKey")
    if not private_key:
        raise ValueError("No private key found in key file")

    # Convert hex string to bytes if needed
    if isinstance(private_key, str):
        # Remove 0x prefix if present
        if private_key.startswith("0x"):
            private_key = private_key[2:]
        # Convert to bytes first, then back to hex string for bittensor
        private_key_bytes = bytes.fromhex(private_key)
        private_key = private_key_bytes.hex()

    return Keypair.create_from_private_key(private_key)


def get_all_hotkeys(wallet_path_str: str) -> list[dict[str, str]]:
    """
    Scan the wallet directory and return a list of all found hotkeys with metadata.
    Returns: list of dicts with keys: wallet_name, hotkey_name, ss58_address
    """
    hotkeys = []
    wallet_path = Path(wallet_path_str)

    if not wallet_path.exists():
        return hotkeys

    # Iterate through all wallet directories
    for wallet_dir in wallet_path.iterdir():
        if not wallet_dir.is_dir():
            continue

        hotkeys_dir = wallet_dir / "hotkeys"
        if not hotkeys_dir.exists() or not hotkeys_dir.is_dir():
            continue

        # Iterate through all hotkey files in the wallet
        for hotkey_file in hotkeys_dir.iterdir():
            try:
                # Skip hidden files
                if hotkey_file.name.startswith("."):
                    continue

                with open(hotkey_file, "r") as f:
                    data = json.load(f)
                    if "ss58Address" in data:
                        hotkeys.append({"wallet_name": wallet_dir.name, "hotkey_name": hotkey_file.name, "ss58_address": data["ss58Address"]})
            except Exception:
                # Skip files that can't be read or parsed
                continue

    return hotkeys
