# Dobby

Dobby is a GitHub bot that offers automated labeling and translation functionalities for your repository.

## Prerequisites

Before installing and using Dobby, make sure you have the following:

### Requirements

-   Python 3.10.x
-   npm

You can install the required dependencies by running the following commands:

bashCopy code

`pip install -r requirements.txt
npm install --global smee-client` 

## Installation

To use Dobby in your GitHub repository, follow these steps:

1.  Clone the repository to your local machine:
    
    
    `git clone https://github.com/beesaferoot/dobby.git` 
    
2.  Install the required dependencies:
    
    
    `pip install -r requirements.txt` 
    
3.  Set up the following environment variables:
    
    -   `APP_ID`: Your GitHub App ID
    -   `PATH_TO_CERT`: The path to your private key certificate file

    
4.  Set up a Cohere API key and add it as an environment variable named `API_KEY`:
    
    
    -   `APP_KEY`: Your Cohere API key 
    
5.  Start the bot:
    
    
    `python3 app.py` 
    

## Usage

Dobby offers two main functionalities: automated labeling and translation.

### Automated Labeling

Dobby can automatically label issues based on the content of the issue using the `embed-multilingual-v2.0` model.

### Translation

To translate an issue, mention Dobby in a comment with the query `@dobby-gh-bot translate to <target-language>`, where `<target-language>` is the target language to be translated to. Dobby will automatically translate the issue into the specified language and post a comment with the translated text. This functionality uses the Cohere generator model `command-xlarge-nightly`.

## Contributing

If you would like to contribute to this project, please open an issue or submit a pull request. All contributions are welcome!