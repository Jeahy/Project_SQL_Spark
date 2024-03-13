import os
import zipfile


def download_data_main(kaggle_username, kaggle_key, download_path, dataset_name, zip_name):
    # Set Kaggle API credentials
    os.environ['KAGGLE_USERNAME'] = kaggle_username
    os.environ['KAGGLE_KEY'] = kaggle_key

    # Create a directory to store the downloaded dataset
    os.makedirs(download_path, exist_ok=True)

    # Use Kaggle CLI to download the dataset
    command = f'kaggle datasets download -p {download_path} {dataset_name}'
    os.system(command)

    # Extract the contents of the downloaded zip file
    zip_file_path = os.path.join(download_path, zip_name)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(download_path)

    # Optionally, remove the downloaded zip file
    os.remove(zip_file_path)
    