import os
import re
import io
import base64

import jinja2
from sanic import Sanic
from sanic.response import html
from PIL import Image, UnidentifiedImageError

from config import cartoon_dir, image_json, cartoon_json


root_dir = r'D:\temp\cartoon'
base_cartoon_path = '/cartoon'


app = Sanic('Cartoon Browser')


@app.route(base_cartoon_path)
async def main_page(request):
    directory_dict = {}
    for cartoon_name in os.listdir(cartoon_dir):
        cartoon_sub_dir = os.path.join(cartoon_dir, cartoon_name)
        cartoon_list = directory_dict.setdefault(cartoon_name, [])

        cartoon_names = []
        for c_name in os.listdir(cartoon_sub_dir):
            if c_name in [cartoon_json]:
                continue
            cartoon_names.append(c_name)

        ordered_names = sorted(cartoon_names, key=lambda x: int(re.match(r'\d+', x).group()))
        for chapter_name in ordered_names:
            chapter_url = '{}/{}'.format(base_cartoon_path, '/'.join([cartoon_name, chapter_name]))
            cartoon_list.append([chapter_name, chapter_url])

    with open('main_template.html') as f:
        template = jinja2.Template(f.read())
        body = template.render(directory_dict=directory_dict, enumerate=enumerate)
    return html(body=body)


@app.route('{}/<cartoon_name>/<chapter_name>'.format(base_cartoon_path))
async def main_page(request, cartoon_name, chapter_name):
    jpeg_header = 'data:image/jpeg;base64,'
    chapter_dir = os.path.join(root_dir, cartoon_name, chapter_name)
    picture_list = []
    for image_name in os.listdir(chapter_dir):
        if image_name in [image_json]:
            continue

        image_path = os.path.join(chapter_dir, image_name)
        try:
            im = Image.open(image_path)
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            buffer = io.BytesIO()
            im.save(buffer, format='jpeg')
            buffer.seek(0)

            data_uri = base64.b64encode(buffer.read()).decode('ascii')
            picture_list.append('{}{}'.format(jpeg_header, data_uri))
        except UnidentifiedImageError:
            os.remove(image_path)

    with open('chapter_template.html') as f:
        template = jinja2.Template(f.read())
        title_name = '{} - {}'.format(cartoon_name, chapter_name)
        body = template.render(title_name=title_name, picture_list=picture_list)
    return html(body=body)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


