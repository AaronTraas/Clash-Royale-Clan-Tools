import logging
import os
import requests
import shutil
import zipfile

logger = logging.getLogger(__name__)

def download_file(url, destination_path):
    # NOTE the stream=True parameter below
    download_status_msg = 'Downloading fan kit: {:,.2f} MB'

    logger.debug(destination_path)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        logger.debug(r.headers)
        with open(destination_path, 'wb') as f:
            counter = 0;
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    counter += 1
                    f.write(chunk)
                    if counter >= 100:
                        download_size = os.path.getsize(destination_path)/(1024*1024)
                        print(download_status_msg.format(download_size), end='\r')
                        counter = 0
                    # f.flush()

        print("\nDownload complete!\n")

def download_fan_kit(tempdir):
    zip_path = os.path.join(tempdir, 'fankit.zip')
    unzip_path = os.path.join(tempdir, 'fankit_unzip')
    dest_path = os.path.join(tempdir, 'fankit')
    try:
        logger.debug('Fankit temp dir = {}'.format(tempdir))

        response = requests.head('https://supr.cl/CRFanKit')
        logger.debug(response.headers)

        if 'Location' in response.headers:
            dropbox_url = response.headers['Location']
            logger.debug(dropbox_url)
            parts = dropbox_url.split('?')
            download_url = parts[0] + '?dl=1'

            download_file(download_url, zip_path)

            print('Unzipping fan kit assets')
            os.mkdir(unzip_path)
            zip_ref = zipfile.ZipFile(zip_path, 'r')
            zip_ref.extractall(unzip_path)
            zip_ref.close()

            print('Copying assets to output folder')
            for subfolder in ['font', 'emotes', 'ui']:
                shutil.copytree(os.path.join(unzip_path, subfolder), os.path.join(dest_path, subfolder))
    except Exception as e:
        logger.error(e)
        logger.error('Could not download Clash Royale Fan Kit')
    finally:
        if os.path.isfile(zip_path):
            os.unlink(zip_path)
        if os.path.isdir(unzip_path):
            shutil.rmtree(unzip_path)

