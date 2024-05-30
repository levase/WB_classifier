import subprocess
import os


def run_file(file_name):
    process = subprocess.Popen(['py', file_name])
    process.wait()


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parse_category = os.path.join(current_dir, 'parse_category.py')
    parse_product_id = os.path.join(current_dir, 'parse_product_id.py')
    parse_description = os.path.join(current_dir, 'parse_description.py')
    
    run_file(parse_category)
    run_file(parse_product_id)
    run_file(parse_description)