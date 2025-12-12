import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import DataManager

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_plants.csv"
        with open(self.test_csv, "w") as f:
            f.write("Plant ID,Plant Name,Plant Scientific Name,Plant O2 Release Data,Plant CO Absorb Data,Short Description of Plant,Recommendation Rating out of 5\n")
            f.write("1,Alpha Plant,Alpha sci,High,High,Desc,5.0\n")
            f.write("2,Beta Plant,Beta sci,Low,Low,Desc,3.5\n")
            f.write("3,Gamma Plant,Gamma sci,Mid,Mid,Desc,4.0\n")
            f.write("4,Zeta Plant,Zeta sci,Mid,Mid,Desc,5.0\n")

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_load_data(self):
        dm = DataManager(self.test_csv)
        self.assertEqual(len(dm.plants), 4)
        self.assertEqual(dm.plants[0].name, "Alpha Plant")
        self.assertEqual(dm.plants[1].rating, 3.5)

    def test_top_10_sorting(self):
        dm = DataManager(self.test_csv)
        top = dm.get_top_10()
        self.assertEqual(top[0].name, "Alpha Plant")
        self.assertEqual(top[1].name, "Zeta Plant")
        self.assertEqual(top[2].name, "Gamma Plant")
        self.assertEqual(top[3].name, "Beta Plant")

    def test_search(self):
        dm = DataManager(self.test_csv)
        results = dm.search("beta")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Beta Plant")

if __name__ == '__main__':
    unittest.main()