
# In the catalog pages, I can retrieve a lot of product specs as JSON via the API, but not all of them.
# Because of this limitation, I decided to make a scraper that works on the product pages, where there is a lot more technical information.
# I chose to use BeautifulSoup and Selenium for most of my code, as there i coudnt use any API on the product pages that provides data in JSON format,
# besides downloading the images and manuals.

import requests
import re
import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


list_cad_download_error =[]
list_manual_download_error =[]

# I've focused on 2 products because the data gathering method is the same for different types of products.
# So it's practically the same, except for the download CAD function, which needs an extra method to deal with some products.
# I chose to use my time on making upgrades to the existing modules, so they can be more robust.
# The get_data method is the same for all the products; it just needs to include the labels in this dictionary and in the format data.


# here i can add any product spec i can gather in the product page. 
products_labels = {
    "AC_MOTORS":{
    "general_purpose": {
        "labels": ["Output @ Frequency", "Catalog Number", "Frame",
                   "Voltage @ Frequency", "Speed", "Product Family", "Phase", "Quantity"]
    },  
    "washdown_duty": {
        "labels": ["Output @ Frequency", "Catalog Number", "Frame",
                   "Voltage @ Frequency", "Speed", "Product Family", "Phase", "Quantity"]
    }
}}


def set_directory():
    try:
        directory = os.path.join(os.getcwd(), "output")
        os.makedirs(directory, exist_ok=True)
        directory = os.path.join(directory, "assets")
        os.makedirs(directory, exist_ok=True)
        
        return directory
    except OSError as e:
        print(f"[ERRO] '{directory}': {e}")
        return None

def create_product_directory(product_name):
    directory = os.path.join(os.getcwd(), "output")
    directory = os.path.join(directory, "assets")
    if product_name:
        directory = os.path.join(directory, product_name)
        os.makedirs(directory, exist_ok=True)
    else:
        directory = os.path.join(directory, 'product_name_not_found')
        os.makedirs(directory, exist_ok=True)
    return directory
    


def get_product_name(product_category,total_pages, page_size=10):
    list_product_codes = []  
    list_image_id = []

    for page_index in range(0, total_pages + 1):  # Vai de 1 até 200
        url = f'https://www.baldor.com/api/products?include=results&language=en-US&pageIndex={page_index}&pageSize={page_size}&category={product_category}'
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85"
        } 

        response = requests.get(url, headers=headers, timeout=10)

        # Using this method, I can get any of the JSON data I need,
        # but I choose to get the specs through the products page as explained before
        if response.status_code == 200:
            data = response.json()
            products = data['results']['matches']

            if not products:  # If there are no more products, break
                break

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

def get_data(url,product_labels,product_type):

    #setting product_data default values to None
    product_data = {key: '' for key in product_labels}
    product_data['name'] = ''
    product_data['Quantity'] = '1'
    product_data['product_name'] =''
    product_data['description'] =''
    print(product_data)  
    
    try:   
        user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85")

        options = Options()
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--headless")  
        options.add_argument("--disable-gpu")

        driver = webdriver.Edge(options=options)   
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

                if label.text in product_labels: 
                    a = str(label.text)
                    product_data[a] = value[div_count].text.strip().replace("\n", "")                     
                div_count +=1   
                
        product_data['name'] = str(product_data['Phase'])+'-Phase' +' '+str(product_type)+' '+str(product_data['Product Family'])
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        
        
    driver.quit()
    
    print(product_data)
    return product_data


def get_cad(url,product_name): 
    try:   
        cad = ''
        
        directory = create_product_directory(product_name)       

        user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85")

        options = Options()
        options.add_argument(f"user-agent={user_agent}")
        prefs = {
        "download.default_directory": directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
        }
        options.add_argument("--headless")  
        options.add_argument("--disable-gpu")
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Edge(options=options)
        url_drawings = url + '#tab="drawings"'
        driver.get(url_drawings)
              
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))     
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".col.span_6_of_12")))
        
        # find the selector for the type of download, ten click it
        download_options = driver.find_element(By.CSS_SELECTOR, ".k-widget.k-dropdown.k-header.ng-pristine.ng-untouched.ng-valid.ng-empty")
        download_options.click()
        
        # select to download a .DWG file
        dwg_option = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, "//li[contains(text(), '2D AutoCAD DWG')]")))       
        dwg_option.click()
        print('DWG selected')

        # setup to avoid ERR_HTTP2_PROTOCOL_ERROR while dowloading CAD file
        # Clear cookies
        driver.delete_all_cookies()        
        # Clear local storage
        driver.execute_script("window.localStorage.clear();")       
        # Clear session storage
        driver.execute_script("window.sessionStorage.clear();")

        # click the download button
        download_button = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".k-button.k-button-icon")))
        download_button.click()
        print('download button clicked')
        
        if "ERR_HTTP2_PROTOCOL_ERROR" in driver.page_source or "Não consigo chegar a esta página" in driver.page_source:    
            if product_name not in list_cad_download_error:
                list_cad_download_error.append(product_name)
                print("❌ Página de erro detectada após o clique no botão de download.")
            driver.quit()
            return list_cad_download_error, cad      
                
        time.sleep(1)     
        
        # verify if DWG was sucessfuly dowloaded
        files = os.listdir(directory)
        dwg_files = [f for f in files if f.endswith(".DWG") and not f.endswith(".crdownload")]

        if not dwg_files:
            print("❌ File not found")

        downloaded_file = dwg_files[0]

        origin = os.path.join(directory, downloaded_file)
        destiny_directory = os.path.join(directory, f"{product_name}_cad.dwg")

        # rename file
        os.rename(origin, destiny_directory)
        cad = str(product_name)+'_cad.dwg'
        
    except Exception as e:        
        if product_name not in list_cad_download_error:
            list_cad_download_error.append(product_name)
            
        print("❌ Erro:", "CAD file unavaliable")   
        driver.quit()
        return list_cad_download_error, cad  
        
        
    driver.quit()
    print('cad',list_cad_download_error)
    return list_cad_download_error, cad     


def get_manual(product_name,mode):    
    manual = ''
    directory = create_product_directory(product_name)   
    url = 'https://www.baldor.com/api/products/'+ product_name +'/infopacket' 
    output_path = os.path.join(directory, f"{product_name}_manual.pdf")
    
    # define hearders
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85"
    }    
    # Request dowload
    response = requests.get(url, headers=headers)

    # mode 1 is retrymode
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"File saved in: {output_path}")
        
    # if clause to not add product_name to the error list if not able to download again    
    elif response.status_code != 200 and mode==1:
        print(f"Dowload error: {response.status_code}")  
        #still not able to download manal
    
    elif response.status_code == 200 and mode==1:
        if list_manual_download_error:
            list_manual_download_error.remove(product_name)
            #download sucessful
    else:        
        list_manual_download_error.append(product_name)
    
    print(list_manual_download_error)
    manual = str(product_name)+'_manual.pdf'
    return list_manual_download_error, manual, directory


def create_url(product_name):
    list_url=[]
    for product in product_name:
        url = 'https://www.baldor.com/catalog/' + product 
        list_url.append(url)

    return list_url


def format_data(product_type, product_data):
    # format the data to proper manipulation and to give to create_json() proper argumnts
    if product_type == 'general_purpose' or product_type == "washdown_duty":
        product_data['product_name'] = str(product_data['product_name'])
        product_data['description'] = str(product_data['description'])         
        catalog_number = re.findall(r'\d+', product_data['Catalog Number'])
        catalog_number = catalog_number[0] if catalog_number else ' ' 
        product_data['Catalog Number'] = str(catalog_number)       
        product_data['Frame'] = str(product_data['Frame'])              
        hp = product_data['Output @ Frequency'].split(' @')[0] 
        hp = re.sub(r'[^\d.]', '', hp)
        if hp.startswith('.'):
            hp = '0' + hp
        hp = re.sub(r'(\.\d*?)0+$', r'\1', hp).rstrip('.')  

        # knowing that this HP is at the especified hertz its a important data
        # but for following the json format as suggeted in the challenge, 
        # and to show how i handle these type of strings, i decided to follow the sugested format.
        # Same for 'Voltage at Frequency'
        product_data['Output @ Frequency'] = str(hp)      
        product_data['Phase'] = str(product_data['Phase'])  
        voltage = "/".join(re.findall(r'(\d+)\.0 V', product_data['Voltage @ Frequency']))
        product_data['Voltage @ Frequency'] = str(voltage) 
        product_data['Speed'] = str(product_data['Speed'].replace(" rpm", ""))

    return product_data


def create_json(product_type,product_data,manual,cad,image): 
    try: 
        # checks if any file wasn't downloaded.
        if manual != '':
            manual = 'assets/'+product_data['product_name']+'/'+manual
        if cad != '':
            cad = 'assets/'+product_data['product_name']+'/'+cad
        if image != '': 
            image = 'assets/'+product_data['product_name']+'/'+'imagem_'+image+'.jpeg'

        # checks if its a empty product_name, if so, doesnt create the json file
        if product_data['product_name'] !='':
            if product_type == 'general_purpose' or product_type == "washdown_duty":
                product_json = {
                'product_id': product_data['product_name'],
                'description': product_data['description'],
                'name': product_data['name'],
                'specs': [
                    {'hp': product_data['Output @ Frequency']},
                    {'voltage': product_data['Voltage @ Frequency']},
                    {'rpm': product_data['Speed']},
                    {'Frame': product_data['Frame']}],
                'bom': [
                    {'part_number': product_data['Catalog Number']},
                    {'description': product_data['Product Family']},
                    {'quantity': product_data['Quantity']}],
                'assets': [
                    {'manual': manual},
                    {'cad': cad},
                    {'image': image}]}
                
                json_name = product_data['product_name'] +'.json'    
                json_path = os.path.join(os.getcwd(), "output", json_name)
                   
                with open(json_path, 'w') as f:
                    json.dump(product_json, f, indent=4)
                    
            else:
                print('empty product name')
    except Exception as e:
        print(f"Error: {e}")       
    return


def get_image(image_id,product_name):
    try:
        url = f'https://www.baldor.com/api/images/{image_id}'
        print(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/135.0.3179.85"}  
        
        if image_id =='' or image_id == '0':
            print('image not available')
    
        response = requests.get(url, headers=headers, timeout=10)
        
        # Verify connection
        if response.status_code == 200:
            
            directory = os.path.join(os.getcwd(), "output")
            directory = os.path.join(directory, "assets")
            print(product_name,' image get')
            if product_name !='':
                directory = os.path.join(directory, product_name)
                os.makedirs(directory, exist_ok=True)
            else:
                directory = os.path.join(directory, 'product_name_not_found')
                os.makedirs(directory, exist_ok=True)
            print(directory)
            
            file_path = os.path.join(directory, f"imagem_{image_id}.jpeg")
            
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            print("Imaged sucessfully downloaded")
        else:
            print(f"Error downloading image. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    return image_id


def process_product(url, image_id, product_labels):
    try:
        product_data = get_data(url, product_labels, 'AC_MOTOR')
        product_name = product_data['product_name']
        manual = get_manual(product_name, 0)[1]

        cad = get_cad(url, product_name)[1]
        image = get_image(str(image_id),str(product_name))

        format_data('general_purpose', product_data)
        create_json('general_purpose',product_data,manual,cad,image)

    except Exception as e:
        print(f"Erro ao processar URL {url}: {e}")

    return 

# Can add a for loop to scrape each product type by using a list of product categories, if desired. 
# For testing purposes, I chose to use 2 product types under the AC MOTORS family

# general purpose and washdown duty
list_family_codes = ['69','16']

if __name__ == "__main__":
    
    # can add anoter loop, to scrape other product_categories

    # loop to scrape AC_MOTORS category
    for family_code in list_family_codes:
        if family_code == '69':
            product_family ='general_purpose'
        elif family_code =='16':
            product_family ='washdown_duty'
            
        product_category = 'AC_MOTORS'
        # product category is the main product family. 16 = Washdown duty
        
        # total pages is how many products request
        # total pages = 0 is 10 products, =1 is 20, and so on, until there is in no more new products
        total_pages = 1
        set_directory()
        
        #gets all products codes
        codes = get_product_name(family_code, total_pages)
        urls = create_url(codes[0])
        
        #get image ID of each product
        image_ids = codes[1]
        #sets the product Group and family, and gets its labels
        product_labels = products_labels[product_category][product_family]['labels']
        
        #flag to monitor run time
        start = time.time()
    
        # Multi threading module
        # Can adjust the max workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for url, image_id in zip(urls, image_ids):
                futures.append(
                    executor.submit(process_product, url, image_id, product_labels)
                )
    
            for future in as_completed(futures):
                future.result()
        
        end = time.time()
        print(f"Total time: {end - start:.2f} seconds")

    # can add retry loop for get_cad, get_manual for missing files, usind mode ==1
