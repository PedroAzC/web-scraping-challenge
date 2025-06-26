from utility import create_product_directory
from web_scraper import general_get_specs, get_manual, get_image, get_cad
# import global_vars


def process_product(product_code, image_id, product_spec):
    product_data = general_get_specs(product_code, product_spec)
    directory = create_product_directory(product_data['product_name'])
    manual_name = get_manual(product_code, directory)
    image_name = get_image(image_id,directory)
    cad_name = get_cad(product_code,directory)
    
    print(product_data)
    print(manual_name)
    print(image_name)
    print(cad_name)
    