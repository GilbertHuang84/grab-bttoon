import os
import json
import logging
import requests

import threadpool

from config import cartoon_dir, image_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('grab_images')


def download_file(url_address, save_path):
    logger.info('Downing {} to {}'.format(url_address, save_path))
    response = requests.get(url_address, stream=True)
    if response.ok:
        with open(save_path, 'wb') as handle:
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        logger.info('Down {} success'.format(url_address))
    else:
        logger.error('Downing error: {}'.format(url_address))


if __name__ == '__main__':
    is_new_picture = True
    pool = threadpool.ThreadPool(5)
    while is_new_picture:
        is_new_picture = False
        for cartoon_name in os.listdir(cartoon_dir):
            cartoon_sub_dir = os.path.join(cartoon_dir, cartoon_name)
            for chapter_name in os.listdir(cartoon_sub_dir):
                chapter_dir = os.path.join(cartoon_sub_dir, chapter_name)
                image_json_path = os.path.join(chapter_dir, image_json)

                image_dict = {}
                if os.path.exists(image_json_path):
                    with open(image_json_path) as f:
                        image_dict = json.load(f)

                for src_path, current_index in image_dict.items():
                    check_src_path = src_path.replace('httpss', 'https').split('?', 1)[0]
                    extend_name = os.path.splitext(check_src_path.rsplit('/', 1)[-1])[-1]
                    export_path = os.path.join(chapter_dir, '{:>02}{}'.format(current_index, extend_name))
                    if not os.path.exists(export_path):
                        is_new_picture = True
                        request = threadpool.WorkRequest(download_file, (check_src_path, export_path))
                        pool.putRequest(request)
        pool.wait()
