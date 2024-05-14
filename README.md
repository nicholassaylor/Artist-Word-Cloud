# Music Artist Word Bubble
### Note: This project is currently still in development. Features may not be fully functional and implementation details are subject to change.

## Description
This program compiles lyrics from music artists on [Genius](https://genius.com/) and creates word clouds using these lyrics.
A word cloud is a visual representation of the frequency of words within a particular work, with more frequent words being larger.
Word clouds can either be in the shape of a particular graphic or simply fill a canvas.

## Using This Software

#### Requirements
* [Python 3.11](https://www.python.org/downloads/release/python-3119/)
  * pip music be installed to install requirements

#### Instructions
1. Download the Program
   * Go to the Releases Tab and Download the Latest Release
2. Run the Executable
   * Double-clicking the program will open the program in a new window and prompt the user for any artists
   * In a terminal, typing `musicwordcloud.exe ["ARTIST_NAME" ... ]` while in the same directory as the program will automatically run the program on the listed artists
   * In either case, output will be in the form of a .png file with the artist name as seen in the link to their artist page on Genius. This will be in a folder named `output_clouds`

## Running from Source

#### Requirements
* [Python 3.11](https://www.python.org/downloads/release/python-3119/)
  * pip must be installed to install requirements

#### Instructions
1. Download the Code
   * This can be done with the green "Code" button near the "About" section on this page
   * Select "Download ZIP", save the file, and unzip the folder
2. Install Requirements
   * Use `pip install -r requirements.txt` to install the required python packages
3. Run the Code
   * Typing `musicwordcloud.py` in your terminal will run the code
   * Artists may be specified through the CLI using the following format:  
     `musicwordcloud.py ["ARTIST_NAME" ... ]`
   * Output will be in the form of a .png file with the artist name as seen in the link to their artist page on Genius. This will be in a folder named `output_clouds`


## FAQs
* Is *insert language here* supported?
  * Currently, the program will accept nearly every language. However, the stopwords used for the cloud creation is limited to only a few of the most popular languages, so results may vary between languages.
* Why are all the lyrics romanized? Are there plans to support other scripts?
  * Due to limitations with the underlying library for the word cloud, only a single script supported at a time. Currently, there are no plans to add this functionality.
* Can I limit the word cloud to a specific album?
  * Not currently, however that is planned to be released at a later date.
* Can I change the colors of the word cloud?
  * Currently, the colors used in the word cloud are randomized. If you do not like the colors generated, you can attempt to generate again, however this may result in a slightly different arrangement of words. The ability to choose your colors may be released at a later date.
* Is there a GUI for this program?
  * Currently, there is not a GUI, but this is anticipated to be added at a later date.
