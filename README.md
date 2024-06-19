# Music Artist Word Bubble
### Note: This project is currently in development. Features may not be fully functional and implementation details are subject to change.

## Description
This program pull lyrics from [Genius](https://genius.com/) for a particular artist and creates a word cloud with their lyrics.
A word cloud is a visual representation of the frequency of words within a particular work, with more frequent words being larger.
Word clouds can either be in the shape of a particular graphic or simply fill a canvas, this program does the latter.

## Using This Software

#### Instructions
1. Download the Program
   * Go to the [Releases Tab](https://github.com/nicholassaylor/Artist-Word-Bubble/releases) and download your desired version of the program
     * `musicwordcloud_cli.exe` is the command line version
     * `musicwordcloud_gui.exe` is the graphical version
2. Run the Executable
   * **Command Line Version**
      * Double-clicking the program will open the program in a new window and prompt the user for artists
        * Opening may take a few seconds and require confirmation from your operating system
      * In a terminal opened in the folder, type `musicwordcloud_cli.exe ["ARTIST_NAME" ... ]` to automatically run the program on the listed artists
      * Output will be in the form of a file named `<artist-name>.png` in a folder named `OutputClouds` where the exe was run
   * **Graphical Interface Version**
     * Double-clicking the program will open the interface to create and save word clouds
       * Opening may take a few seconds and require confirmation from your operating system
     *  You will be prompted to choose the location of your saved files

## Running from Source

#### Requirements
* [Python 3.11](https://www.python.org/downloads/release/python-3119/)
  * pip must be installed to install requirements
  * Python should be added to your PATH if prompted

#### Instructions
1. Download the Code
   * Go to the [Releases Tab](https://github.com/nicholassaylor/Artist-Word-Bubble/releases) and Download the Latest Release
   * Select "Source code (zip)", save the file, and unzip the folder
2. Install Requirements
   * Use `pip install -r requirements.txt` to install the required python packages
3. Running the Code
   * **Command Line Version** 
     * Typing `python.exe musicwordcloud/musicwordcloud.py` in a terminal opened in the project folder or opening the file directly in Python will run the command line interface
     * Artists may be specified through the CLI using the following format:  
     `python.exe musicwordcloud/musicwordcloud.py ["ARTIST_NAME" ... ]`
     * Output will be in the form of a file named `<artist-name>.png` in a folder named `OutputClouds` where the code was run
   * **Graphical Interface Version**
     * Typing `python.exe musicwordcloud/gui.py` in a terminal opened in the project folder or opening the file directly in Python will run the graphical interface to interact with
     * Specifying artists through the command line is not supported
     * You will be prompted to choose the location of your saved files

## FAQs
* Is *insert language here* supported?
  * While the program will be able to put out a word cloud for virtually every language, however less widely used languages may contain common stopwords such as articles and prepositions.
* Why are all the lyrics romanized? Are there plans to support other scripts?
  * Due to limitations with the underlying systems, only a single script supported at a time. Currently, there are no plans to add this functionality.
* Can I limit the word cloud to a specific album?
  * Not currently, however that is planned to be released at a later date.
