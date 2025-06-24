from utility import create_product_directory
from web_scraper import general_get_specs, get_manual

def process_product(product_code, product_spec):
    product_data = general_get_specs(product_code, product_spec)
    directory = create_product_directory(product_data['product_name'])
    manual_name = get_manual(product_code, directory)
    print(product_data)
    print(manual_name)