# Sleuth Reporting

A small app to pull data from Sleuth.io.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/username/project.git
    ```

1. Create and activate a virtual environment:

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

1. Install the dependencies:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Set up the required environment variables. Create a `.env` file in the root directory of the project and add the necessary variables. 
For example:
    ```plaintext
    SLEUTH_PERSONAL_TOKEN=(your personal sleuth token)
    ```
1. Run the application:

    ```shell
    python main.py
    ```
    pulls all the stuff and writes it to an excel in your CWD.


## Environment Variables

`SLEUTH_PERSONAL_TOKEN`
This is the token used for API access. Get it from https://app.sleuth.io/account/personal_tokens.

`ORG_SLUG` 
This is the organization slug for your organization.

## Contributing



## License


