from concurrent.futures import ThreadPoolExecutor, as_completed

# created libraries for the project
from web_scraper import get_product_ids
# from utility import create_product_directory
from multi_thread_module import process_product
import global_vars

class AC_motor:

    def __init__(self,type, sub_type, sub_sub_type):
        self.type = type
        self.sub_type = sub_type
        self.sub_sub_type = sub_sub_type
        self.product_web_page_code = list(global_vars.dict_ac_motors_general_purpose[self.sub_sub_type].keys())[0]
        self.product_specs = list(global_vars.dict_ac_motors_general_purpose[self.sub_sub_type][self.product_web_page_code])

MAX_THREADS = 10

if __name__ == '__main__':

    list_product_web_page_code = [110, 312]
    list_sub_sub_type = ["Three Phase Enclosed","Single Phase Enclosed"]
    # list_product_web_page_code = [110]
    # list_sub_sub_type = ["Three Phase Enclosed"]

    for sub_sub_type in list_sub_sub_type:
        product_spec = []
        product_web_page_code = list(global_vars.dict_ac_motors_general_purpose[sub_sub_type].keys())[0]
        print(product_web_page_code)
        
        product_spec = global_vars.dict_ac_motors_general_purpose[sub_sub_type][product_web_page_code]
        print(product_spec)

        list_product_codes, list_image_id = get_product_ids(product_web_page_code)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # for product_code in list_product_codes:
            for product_code,image_id in zip(list_product_codes, list_image_id):
                futures.append(executor.submit(process_product, product_code, image_id, product_spec))

            for future in as_completed(futures):
                future.result()  # Captura possíveis exceções

