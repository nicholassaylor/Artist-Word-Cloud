# Music Artist Word Bubble
### Note: This project is currently in development. Features may not be fully functional and implementation details are subject to change.

## Description
This program pull lyrics from [Genius](https://genius.com/) for a particular artist and creates a word cloud with their lyrics.
A word cloud is a visual representation of the frequency of words within a particular work, with more frequent words being larger.
Word clouds can either be in the shape of a particular graphic or simply fill a canvas, this program does the latter.

## Using This Software

#### Instructions
1. Download the Program
   * Go to the [Releases Tab](https://github.com/nicholassaylor/Artist-Word-Bubble/releases) and Download the Latest Release
2. Run the Executable
   * Double-clicking the program will open the program in a new window and prompt the user for artists
     * Opening may take a few seconds
   * In a terminal opened in the folder, type `musicwordcloud.exe ["ARTIST_NAME" ... ]` to automatically run the program on the listed artists
   * Output will be in the form of a file named `<artist-name>.png` in a folder named `OutputClouds` where the exe was run

## Running from Source

#### Requirements
* [Python 3.11](https://www.python.org/downloads/release/python-3119/)
  * pip must be installed to install requirements

#### Instructions
1. Download the Code
   * Go to the [Releases Tab](https://github.com/nicholassaylor/Artist-Word-Bubble/releases) and Download the Latest Release
   * Select "Source code (zip)", save the file, and unzip the folder
2. Install Requirements
   * Use `pip install -r requirements.txt` to install the required python packages
3. Run the Code
   * Typing `python.exe musicwordcloud.py` in a terminal opened in the project folder will run the code
   * Artists may be specified through the CLI using the following format:  
     `python.exe musicwordcloud.py ["ARTIST_NAME" ... ]`
   * Output will be in the form of a file named `<artist-name>.png` in a folder named `OutputClouds` where the code was run


## FAQs
* Is *insert language here* supported?
  * While the program will be able to put out a word cloud for virtually every language, however less widely used languages may contain common stopwords such as articles and prepositions.
* Why are all the lyrics romanized? Are there plans to support other scripts?
  * Due to limitations with the underlying systems, only a single script supported at a time. Currently, there are no plans to add this functionality.
* Can I limit the word cloud to a specific album?
  * Not currently, however that is planned to be released at a later date.
* Is there a GUI for this program?
  * Currently, there is not a GUI, but this is anticipated to be added at a later date.
