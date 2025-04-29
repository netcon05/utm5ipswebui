# utm5ipswebui
Free (unallocated) ip addresses from UTM5 Billing system

## Installation
The setup instructions will be based on the Debian GNU/Linux distribution

- Install needed packages

    `sudo apt install python3-pip python3-venv git`

- Clone the repository

    `git clone https://github.com/netcon05/utm5ipswebui.git`

- Enter the folder

    `cd utm5ipswebui`

- Create virtual environment

    `python3 -m venv .venv`

- Activate virtual environment

    `source .venv/bin/activate`

- Upgrade pip

    `pip3 install --upgrade pip`

- Install all required packages

    `pip3 install -r requirements.txt`

- Make needed changes to config.json file

    `nano config.json`

- Run the application

    `python3 app.py`
