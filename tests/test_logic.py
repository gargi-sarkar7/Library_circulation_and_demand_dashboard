import unittest, tempfile
from pathlib import Path
import pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from library_dashboard import load_and_clean, LoanRecord

class ProjectTests(unittest.TestCase):
    def test_duplicates_and_missing_values(self):
        sample = pd.DataFrame([
            ['X1','B1','Book','Fiction','U1','2025-01-01','2025-01-08',''],
            ['X1','B1','Book','Fiction','U1','2025-01-01','2025-01-08',''],
            ['X2','B2','Other','','','2025-01-02','2025-01-09','']
        ], columns=['record_id','book_id','book_title','category','borrower_id','loan_date','due_date','return_date'])
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f: sample.to_csv(f.name,index=False)
        clean, quality = load_and_clean(f.name)
        self.assertEqual(len(clean),2); self.assertEqual(quality['duplicate_record_ids_removed'],1)
        self.assertEqual(clean.iloc[1]['category'],'Unknown'); self.assertEqual(clean.iloc[1]['borrower_id'],'Unknown')
    def test_duration_special_method(self):
        obj=LoanRecord('X','B','Book','Fiction','U','2025-01-01','2025-01-08','2025-01-05')
        self.assertEqual(len(obj),4)
if __name__=='__main__': unittest.main()
