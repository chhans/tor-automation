# Website Fingerprinting Attack on Tor Client Anonymity

## What

* Scripts to automatically visit web sites through Tor and capture the data.
* Scripts to extract information such as the number of Tor cells from the pcaps.
* Scripts to train classifiers with information and subsequently predict which pages and sites was visited from this information.

## Setup

The scripts are made to run on Ubuntu with Tor version 0.2.5.10 and Mozilla Firefox 37.0.1, but may work on other setups as well.

## Capture web pages

# Dependencies

* Selenium WebDriver Python module
* PyVirtualDisplay Python module
* Tshark

# Usage

1. Edit torProfile.py to match setup if your loopback interface or Tor port differs from the default 127.0.0.1:9050.
2. Run capture.py with the following arguments:
*capture.py <web page list> <number of pages from list to visit> <network interface> <training data (0/1)>* 