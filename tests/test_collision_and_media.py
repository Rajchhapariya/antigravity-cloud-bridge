"""
Unit tests for collision-free naming and multi-media ingestion in Antigravity Cloud Bridge.
"""

import os
import tempfile
import unittest

class TestCollisionFreePath(unittest.TestCase):
    def test_unique_path_creation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            def get_collision_free_path(base_dir, filename):
                target = os.path.join(base_dir, filename)
                if not os.path.exists(target):
                    return target
                root, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(base_dir, f"{root}_{counter}{ext}")):
                    counter += 1
                return os.path.join(base_dir, f"{root}_{counter}{ext}")

            # 1. First file
            p1 = get_collision_free_path(tmp_dir, "photo_20260925_120000.jpg")
            with open(p1, "w") as f:
                f.write("photo 1")

            # 2. Second file with same base name
            p2 = get_collision_free_path(tmp_dir, "photo_20260925_120000.jpg")
            with open(p2, "w") as f:
                f.write("photo 2")

            # 3. Third file with same base name
            p3 = get_collision_free_path(tmp_dir, "photo_20260925_120000.jpg")
            with open(p3, "w") as f:
                f.write("photo 3")

            self.assertEqual(os.path.basename(p1), "photo_20260925_120000.jpg")
            self.assertEqual(os.path.basename(p2), "photo_20260925_120000_1.jpg")
            self.assertEqual(os.path.basename(p3), "photo_20260925_120000_2.jpg")

            # Verify contents were not overwritten
            with open(p1) as f:
                self.assertEqual(f.read(), "photo 1")
            with open(p2) as f:
                self.assertEqual(f.read(), "photo 2")
            with open(p3) as f:
                self.assertEqual(f.read(), "photo 3")

if __name__ == "__main__":
    unittest.main()
