def create_product_directory(product_name):
    try:
        directory = os.path.join(os.getcwd(), "output")
        directory = os.path.join(directory, "assets")
        if product_name:
            directory = os.path.join(directory, product_name)
            os.makedirs(directory, exist_ok=True)
        else:
            directory = os.path.join(directory, 'product_name_not_found')
            os.makedirs(directory, exist_ok=True)
        return directory
    
    except OSError as e:
        print(f"[ERRO] '{directory}': {e}")
        return None