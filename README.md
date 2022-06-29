# Drawception Image Scraper

This is a simple python script that scrapes the drawing panels of any user on Drawception (main or stage). 
Automatically browses through 100 pages of user public games and saves any image by the user. Also saves a csv
file of basic details of each panel downloaded.

## Usage
`python3 scraper.py http://www.drawception.com/player/[id]/[name]`

Images are saved to ./images/ directory by default. Pass in a  `-d [your directory]` flag to change 
where the images are saved. 
