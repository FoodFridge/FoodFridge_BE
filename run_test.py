import unittest

class TestAWSGIImport(unittest.TestCase):
    def test_awsgi_import(self):
        # Open run.py and read its contents
        with open('run.py', 'r') as file:
            contents = file.read()

        # Check if "import awsgi" is in the file contents
        # This is a simple check and assumes the import statement is not commented out.
        # It does not account for multiline comments or conditional imports within code blocks.
        self.assertIn('import awsgi', contents, "awsgi must be imported in run.py")

if __name__ == '__main__':
    unittest.main()