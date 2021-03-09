## grab bttoon
This package has a toolset of iterating the web from [bttoon](www.bttoon.com), grabbing the images and provide 
a simple HTTP server for viewing the downloaded image data.

Since it has too much AD in that website, and quite a bad experience of viewing those images, then I made this toolset. 
Anyway all the issues I met, already solved in the Internet. Thanks for the internet. I just shared my experience.

## Requests

* selenium 
* chrome driver
* threadpool
* jinja2
* sanic
* PIL

## How to run

1. Download the src file from github

2. Change the config file

Basically we need to change the *cartoon_dir* and *chrome_driver_path* in the *config.py*

3. Run the script saving all the image link into the setting files

`python grab_image_links.py`

4. Run the script saving all the images from the setting files

`python grab_images.py`

5. Run the script serving the web server

`python http_server.py`

