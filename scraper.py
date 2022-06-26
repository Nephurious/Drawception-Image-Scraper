import time
from drawception_image_panel import DrawceptionImagePanel
from drawception_player import DrawceptionPlayer
import argparse
import pandas as pd
import logging
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads Drawception Images of the player given the player url.")
    parser.add_argument('url', type=str, help="Player url")
    parser.add_argument('-d', '--directory', default='./images/', type=str, help="Directory to save the images in")
    parser.add_argument('-l', '--log', action='store_true', help="Enables the logging of DEBUG and INFO to the file \"scraper.log\"")
    args = parser.parse_args()
    if args.log:
        logging.basicConfig(filename='scraper.log', level=logging.DEBUG, filemode='w')
    if not os.path.isdir(args.directory):
        raise FileNotFoundError("No such or invalid directory: {}".format(args.directory))
    player = DrawceptionPlayer(args.url)
    player.set_player_details()
    links = player.scrape_drawing_links()
    player_panels = []
    panel_df_rows = []
    for link in links:
        panel = DrawceptionImagePanel(link)
        panel.set_panel_details()
        player_panels.append(panel)
        panel_df_rows.append(panel.get_panel_details())
        logging.info("Processed {}".format(link))
        time.sleep(2)
    panel_df = pd.DataFrame(panel_df_rows, columns=['id','name',
            'name_file_safe','author','creation_date','time_spent',
            'panel_url'])
    panel_df.to_csv("{}_panels.csv".format(player.name_filesafe), index=False)
    for panel in player_panels:
        image_src = panel.image_src
        if len(image_src) > 100:
            image_src = image_src[:100] + '...'
        logging.info("Downloading {}".format(image_src))
        panel.download_drawing(directory=args.directory)
        time.sleep(2)