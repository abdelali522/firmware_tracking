import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


@dataclass
class Block:
    index: int
    timestamp: str
    version_name: str
    firmware_hash: str
    previous_hash: str
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "version_name": self.version_name,
                "firmware_hash": self.firmware_hash,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "version_name": self.version_name,
            "firmware_hash": self.firmware_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Block":
        return cls(
            index=int(payload["index"]),
            timestamp=str(payload["timestamp"]),
            version_name=str(payload["version_name"]),
            firmware_hash=str(payload["firmware_hash"]),
            previous_hash=str(payload["previous_hash"]),
            hash=str(payload.get("hash", "")),
        )


class Blockchain:
    def __init__(self, storage_path: str | Path = "data/firmware_chain.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.chain: list[Block] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.chain = []
            return
        if not isinstance(data, list):
            self.chain = []
            return
        self.chain = [Block.from_dict(entry) for entry in data]

    def _save(self) -> None:
        self.storage_path.write_text(
            json.dumps([block.to_dict() for block in self.chain], indent=2),
            encoding="utf-8",
        )

    def add_version(self, version_name: str, firmware_path: str | Path) -> Block:
        firmware_file = Path(firmware_path)
        if not firmware_file.exists():
            raise FileNotFoundError(f"Firmware file not found: {firmware_file}")

        previous_hash = self.chain[-1].hash if self.chain else "GENESIS"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        firmware_hash = sha256(firmware_file.read_bytes()).hexdigest()

        block = Block(
            index=len(self.chain),
            timestamp=timestamp,
            version_name=version_name,
            firmware_hash=firmware_hash,
            previous_hash=previous_hash,
        )
        self.chain.append(block)
        self._save()
        return block

    def find_version(self, value: str) -> dict[str, Any] | None:
        query = str(value).strip().lower()
        for block in self.chain:
            if query in block.version_name.lower() or query == str(block.index):
                return block.to_dict()
        return None

    def list_versions(self) -> list[dict[str, Any]]:
        return [block.to_dict() for block in self.chain]

    def verify_chain(self) -> dict[str, Any]:
        if not self.chain:
            return {"valid": True, "blocks_checked": 0, "message": "No firmware versions recorded."}

        for index, block in enumerate(self.chain):
            expected_hash = block.compute_hash()
            if block.hash != expected_hash:
                return {
                    "valid": False,
                    "broken_block": index,
                    "reason": "The block hash does not match its content.",
                    "hash": block.hash,
                    "expected_hash": expected_hash,
                }

            if index > 0:
                previous_block = self.chain[index - 1]
                if block.previous_hash != previous_block.hash:
                    return {
                        "valid": False,
                        "broken_block": index,
                        "reason": "The block linkage with the previous block has been altered.",
                        "previous_hash": block.previous_hash,
                        "expected_previous_hash": previous_block.hash,
                    }

        return {"valid": True, "blocks_checked": len(self.chain), "message": "The chain is valid."}

    def tamper_block(self, version_name: str) -> Block:
        for block in self.chain:
            if block.version_name == version_name:
                last = block.firmware_hash[-1]
                altered = "0" if last != "0" else "1"
                block.firmware_hash = block.firmware_hash[:-1] + altered
                block.hash = block.compute_hash()
                self._save()
                return block
        raise ValueError(f"Version '{version_name}' was not found in the blockchain.")


def _build_parser() -> Any:
    import argparse

    parser = argparse.ArgumentParser(description="Local blockchain prototype for firmware version tracking.")
    parser.add_argument("--storage", default="data/firmware_chain.json", help="Path to the JSON chain file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-version", help="Add a new firmware version to the blockchain.")
    add_parser.add_argument("firmware_path", help="Path to the firmware file to be registered.")
    add_parser.add_argument("--name", required=True, help="Version label, for example v1.0 or release-2025-01.")

    list_parser = subparsers.add_parser("list", help="Display the recorded firmware versions.")
    list_parser.add_argument("--json", action="store_true", help="Print JSON output.")

    search_parser = subparsers.add_parser("search", help="Search for a version by name or block number.")
    search_parser.add_argument("query", help="Version name or index to search.")

    verify_parser = subparsers.add_parser("verify", help="Check the integrity of the full chain.")
    tamper_parser = subparsers.add_parser("tamper", help="Simulate an alteration in a chosen version and break the chain.")
    tamper_parser.add_argument("version_name", help="Version name to corrupt.")

    return parser


def main() -> None:
    import sys

    parser = _build_parser()
    args = parser.parse_args()

    blockchain = Blockchain(args.storage)

    if args.command == "add-version":
        block = blockchain.add_version(args.name, args.firmware_path)
        print(f"Version '{args.name}' added to block {block.index}.")
        print(json.dumps(block.to_dict(), indent=2))
    elif args.command == "list":
        versions = blockchain.list_versions()
        if args.json or not versions:
            print(json.dumps(versions, indent=2))
        else:
            for block in versions:
                print(f"#{block['index']} - {block['version_name']} | sha256={block['firmware_hash'][:12]} | hash={block['hash'][:12]}")
    elif args.command == "search":
        result = blockchain.find_version(args.query)
        if result is None:
            print(f"No version matching '{args.query}' was found.")
        else:
            print(json.dumps(result, indent=2))
    elif args.command == "verify":
        print(json.dumps(blockchain.verify_chain(), indent=2))
    elif args.command == "tamper":
        try:
            block = blockchain.tamper_block(args.version_name)
            print(f"Version '{args.version_name}' was altered in block #{block.index}.")
            print(json.dumps(blockchain.verify_chain(), indent=2))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
