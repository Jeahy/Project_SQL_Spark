import os
import zipfile

def download_data_main():
    # Set Kaggle API credentials
    os.environ['KAGGLE_USERNAME'] = "jessfriedrichshain"
    os.environ['KAGGLE_KEY'] = "2d5ae588b5dd2282a7c0750231c96fb3"

    # Specify the dataset you want to download
    dataset_name = 'carrie1/ecommerce-data'

    # Create a directory to store the downloaded dataset
    download_path = '/home/pkn/ecompipeline/data'
    os.makedirs(download_path, exist_ok=True)

    # Use Kaggle CLI to download the dataset
    command = f'kaggle datasets download -p {download_path} {dataset_name}'
    os.system(command)

    # Extract the contents of the downloaded zip file
    zip_file_path = os.path.join(download_path, f'ecommerce-data.zip')
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(download_path)

    # Optionally, remove the downloaded zip file
    os.remove(zip_file_path)