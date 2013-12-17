DNS Analysis Scripts
==========

A collection of scripts used to detect Fast-Flux domains and DGA domains.

Based on research conducted for MSc thesis, related research papers are available from the following locations:
*[ISSA 2011](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6027531 "A framework for DNS based detection and mitigation of malware infections on a network")
*[ISSA 2012](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6320433 "Geo-spatial autocorrelation as a metric for the detection of Fast-Flux botnet domains")
*[Botconf 2013](https://www.botconf.eu/wp-content/uploads/2013/08/09-EtienneStalmans-paper.pdf "Spatial Statistics as a Metric for Detecting Botnet C2 Servers")

Basic Usage
==========

To analyse a single domain:
python FFAnalyse.py -d exampledomain.com

To analyse multple domains:
cat domains.txt | xargs -I {} python FFAnalyse.py -d {}

