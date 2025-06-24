import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import global_vars

def get_product_ids(product_web_page_code):
    
    list_product_codes = []  
    list_image_id = []
    page_size=10

    url = f'https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize={page_size}&category={product_web_page_code}'
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85"
        } 
    
    response = requests.get(url, headers=headers, timeout=10)

    # Using this method, I can get any of the JSON data I need,
    # but I choose to get the specs through the products page as explained before
    if response.status_code == 200: # gets how many products are in the page
        data = response.json()
        total_products = data['results']['count']
        
        total_json_files = (total_products + page_size-1) // page_size # make so it aways gets all products. If total product = 131, it will run 14 times, if page_size=10
    
    else:
        print(f"Error {page_index}: {response.status_code}")  


    # manual value insert, for tests
    total_json_files = 1
    for page_index in range(0,total_json_files): 

        # https://www.baldor.com/api/products?include=results&language=en-US&pageIndex={page_index}&pageSize=10&category=110
        url = f'https://www.baldor.com/api/products?include=results&language=en-US&pageIndex={page_index}&pageSize={page_size}&category={product_web_page_code}'

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            products = data['results']['matches']

            if not products:  # If there are no more products, break
                print('no more products')
            for product in products:
                product_code = product.get("code")
                image_id = product.get("imageId")
                
                if product_code:
                    list_product_codes.append(product_code)
                else:
                    list_product_codes.append('')
                if image_id:
                    list_image_id.append(str(image_id))
                else:
                    print('erro pegar img id')
                    list_image_id.append('')
                    
            print(f"Page {page_index} loaded successfully.")
        else:
            
            print(f"Error {page_index}: {response.status_code}")
            break  
        
    return list_product_codes, list_image_id

def get_manual(product_code,directory):
    
    manual = ''   
    url = 'https://www.baldor.com/api/products/'+ product_code +'/infopacket' 
    output_path = os.path.join(directory, f"{product_code}_manual.pdf")
    
    # define hearders
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85"
    }    
    # Request dowload
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
            print(f"File saved in: {output_path}")
        
    else:        
        global_vars.error_log_manual_download.append(product_code)
    
    print(global_vars.error_log_manual_download)
    
    return manual

def general_get_specs(product_code,product_specs):

    product_data = {}
    product_data['name'] = ''
    product_data['Quantity'] = '1'
    product_data['product_name'] =''
    product_data['description'] = ''  
    
    url =f'https://www.baldor.com/catalog/{product_code}'

    try:   
        user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85")

        options = Options()
        options.add_argument(f"user-agent={user_agent}")
        # options.add_argument("--headless")  
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)   
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))       
        html = driver.page_source      
        soup = BeautifulSoup(html, 'html.parser')

        product_name = soup.find('div',class_='page-title')
        product_data['product_name'] = str(product_name.text.strip().replace("\n", ""))      

        description = soup.find('div',class_='product-description')
        product_data['description'] = str(description.text.strip().replace("\n", ""))           
        data = soup.find_all('div', class_='col span_1_of_2')

        # create a loop for the 2 columns specs
        for d in data[0:2]:
            labels = d.find_all('span',class_='label')

            value = d.find_all('span',class_='value')
            div_count = 0
            for label in labels:
                # print('label inicio ->', label)

                if label.text in product_specs: 
                    # print('label text ->', label.text)
                    a = str(label.text)
                    product_data[a] = value[div_count].text.strip().replace("\n", "")                     
                div_count +=1   
                
        product_data['name'] = str(product_data['Phase']) +'-Phase' + ' ' + str(product_code) + ' '
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        
        
    driver.quit()
    
    print(product_data)
    return product_data
