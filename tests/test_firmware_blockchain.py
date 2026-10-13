import tempfile
import unittest
from pathlib import Path

from firmware_blockchain import Blockchain


class BlockchainTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.storage = self.root / "firmware_chain.json"
        self.blockchain = Blockchain(self.storage)

        self.firmware_v1 = self.root / "firmware_v1.bin"
        self.firmware_v1.write_bytes(b"version_1_payload")

        self.firmware_v2 = self.root / "firmware_v2.bin"
        self.firmware_v2.write_bytes(b"version_2_payload")

        self.firmware_v3 = self.root / "firmware_v3.bin"
        self.firmware_v3.write_bytes(b"version_3_payload")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_version_and_verify_chain(self):
        self.blockchain.add_version("v1.0", self.firmware_v1)
        self.blockchain.add_version("v2.0", self.firmware_v2)
        self.blockchain.add_version("v3.0", self.firmware_v3)

        result = self.blockchain.verify_chain()

        self.assertTrue(result["valid"])
        self.assertEqual(result["blocks_checked"], 3)

    def test_search_version_by_name(self):
        self.blockchain.add_version("v1.0", self.firmware_v1)
        self.blockchain.add_version("v2.0", self.firmware_v2)

        result = self.blockchain.find_version("v2.0")

        self.assertIsNotNone(result)
        self.assertEqual(result["version_name"], "v2.0")

    def test_tamper_breaks_chain_integrity(self):
        self.blockchain.add_version("v1.0", self.firmware_v1)
        self.blockchain.add_version("v2.0", self.firmware_v2)

        self.blockchain.tamper_block("v1.0")
        result = self.blockchain.verify_chain()

        self.assertFalse(result["valid"])
        self.assertEqual(result["broken_block"], 1)


if __name__ == "__main__":
    unittest.main()
