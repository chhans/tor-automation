# Website Fingerprinting Attacks on Tor Client Anonymity

## What

* Scripts to automatically visit web sites through Tor and capture the data.
* Scripts to extract information such as the number of Tor cells from the pcaps.
* Scripts to train classifiers with information and subsequently predict which pages and sites was visited from this information.

## Setup

The scripts are made to run on Ubuntu with Python 2.7, Tor version 0.2.5.10 and Mozilla Firefox 37.0.1, but may work on other setups as well.

## Capture web pages

### Dependencies

* Selenium WebDriver Python module
* PyVirtualDisplay Python module
* Tshark

### Usage

1. Edit torProfile.py to match setup if your loopback interface or Tor port differs from the default 127.0.0.1:9050.
2. Run capture.py with the following arguments:
*capture.py &lt;web page list&gt; &lt;number of pages from list to visit&gt; &lt;network interface&gt; &lt;training data (0/1)&gt;* OR
*capture.py manual &lt;network interface&gt; &lt;training data (0/1)&gt &lt;web page(s)&gt;*

#### Examples

*capture.py alexa.csv 1000 eth0 1*
Capture page loads for the *1000* first pages listed in *alexa.csv* on interface *eth0* and stores it in folder for *training data* (./Dumps/training/&lt;url&gt;/i.cap).

*capture.py manual eth0 1 google.com youtube.com*
Capture page loads for the sites *google.com* and *youtube.com* on interface *eth0* and stores it in folder for *training data*.

## Generate fingerprints for page loads

Generates the fingerprints for all pcap files in ./Dumps/* containing the number of Tor uploaded and the number of Tor cells downloaded.

### Dependencies

* pcapy Python module

### Usage

*fingerprint.py &lt;IP address of client&gt;*

## Basic website fingerprinting attack experiments

Trains classifiers and runs experiments in the form of predictions of web pages based on the fingerprint of said web page. Stores result of each experiment in ./BasicResults/

### Usage

The number of fingerprints stored in each web page folder should be equal to the number of training instances + the number of experiment fingerprints for each page.

*basicexperiment.py &lt;number of training instances&gt; &lt;number of experiment fingerprints for each page&gt;*

## Capture a two-minute interval of browsing web sites

### Dependencies

* Selenium WebDriver Python module
* Tshark

### Usage

*patterncapture.py &lt;open/closed&gt; &lt;number of visits (given open world)&gt;*

#### Examples

*patterncapture.py closed*
Opens a browser window for each web site in the specified urls array (http://cbsnews.com, http://google.com, http://nrk.no, http://vimeo.com, http://wikipedia.org, http://youtube.com), keeping the browser window for each site open for 2 minutes. The captured traffic is stored in ./PatternDumps/closed/&lt;url&gt;/i.cap.

*patterncapture.py open 10*
Does the same for the 10 first sites in openlist.csv and stores the captured traffic in ./PatternDumps/open/&lt;url&gt;/i.cap.

## Generate fingerprints for sites browsed

Generates the fingerprints for all pcap files in ./PatternDumps/* containing a feature vector of dimension 6.

### Dependencies

* pcapy Python module with modified source code for nanosecond accuracy

In the source code of pcapy (version 0.10.2 in my case), edit the following line in pcapy.cc

*pt = pcap_open_offline_with_tstamp_precision(filename, PCAP_TSTAMP_PRECISION_NANO, errbuff);*

### Usage

*patternfingerprint.py &lt;IP address of client&gt;*

## Browsing pattern based web *site* fingerprinting attack experiments

### Usage

*patternexperiment.py &lt;closed/open&gt; &lt;number of training instances&gt; &lt;number of experiment fingerprints for each classified web site&gt; &lt;marked sites (given open world&gt;*

### Examples

*patterexperiment.py closed 4 2*
For all combinations of 4 training instances out of 6 (4+2) fingerprints, train a classifier with 4 feature vectors/fingerprints for each site and do predictions on the remaining 2. Stores the result in ./PatternResults/closed/

*patternexperiment.py open 4 2 cbsnews.com vimeo.com*
For all combinations of 4 training instances out of 6 (4+2) fingerprints, train a classifier with 4 feature vectors/fingerprints for each site included in (http://cbsnews.com, http://google.com, http://nrk.no, http://vimeo.com, http://wikipedia.org, http://youtube.com). Do predictions on all the remaining fingerprints in both ./PatternDumps/closed/ and ./PatternDumps/open/