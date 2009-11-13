#!/usr/bin/env python 

import sys, cgitb, site

# To pretty-print exceptions.
cgitb.enable()

# Add our local packages to the path
site.addsitedir('/societies/cuspaceflight/python-packages/')

import logging, demjson, uuid, os, subprocess, StringIO

# Logging support
log = logging.getLogger('main')
console = logging.StreamHandler(sys.stdout)
console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
log.addHandler(console)
log_string_stream = StringIO.StringIO()
string_handler = logging.StreamHandler(log_string_stream)
string_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
log.addHandler(string_handler)
log.setLevel(logging.INFO)

def _custom_except_hook(*exc_info):
	print "Content-Type: text/html"
	print "Status: 400 Bad Request"
	print
	print "<!DOCTYPE html>"
	print "<html>"
	print "<head><title>Bad request</title></head>"
	print "<body>"
	try:
		print "<h1>Log</h1>"
		print "<pre>"+log_string_stream.getvalue()+"</pre>"
	except:
		pass
	print "<h1>Exception</h1>"
	cgitb.handler(exc_info)
	print "</body>"
	print "</html>"
	sys.exit(1)

def output_to_kml(infilename, kmlfilename):
	kml_header = """<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
<name>CUSF Landing Prediction</name>
<Placemark>
  <name>Flight Path</name>
  <Style>
    <LineStyle>
      <color>FF0000FF</color>
      <width>4</width>
    </LineStyle>
	<PolyStyle id="khPolyStyle810">
		<color>7f00ff00</color>
	</PolyStyle>
  </Style>
  <LineString>
    <tessellate>1</tessellate>
    <extrude>0</extrude>
    <altitudeMode>absolute</altitudeMode>
    <coordinates>"""
    	kml_footer = """
    </coordinates>
  </LineString>
</Placemark>
</Document>
</kml>"""

	infile = open(infilename, 'r')
	outfile = open(kmlfilename, 'w')

	outfile.write(kml_header)
	for line in infile:
		fields = line.split(',')
		outfile.write(','.join(map(lambda x: fields[x], (2,1,3))) + '\n')
	outfile.write(kml_footer)


def main():
	# Create a UUID for the prediction
	pred_uuid = uuid.uuid4()

	# Create a directory for the predicition result.
	pred_root = os.path.join('/societies/cuspaceflight/public_html/predict_rjw/landpred/predictions/', str(pred_uuid))
	os.mkdir(pred_root)

	log_file = open(os.path.join(pred_root, 'log'), 'w')
	new_console = logging.StreamHandler(log_file)
	new_console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
	log.removeHandler(console)
	log.addHandler(new_console)

	# Trap exceptions and print them to the log
	sys.excepthook = _custom_except_hook

	log.info('CUSF landing predictor')

	# Read the scenario posted
	scenario = sys.stdin.readlines()

	log.info('Scenario read:')
	for line in scenario:
		log.info(line.rstrip())

	# Parse the scenario
	try:
		scenario = demjson.decode(''.join(scenario))
	except:
		log.error('Could not parse scenario')

	log.info('Parsed scenario:')
	log.info(scenario)

	# Convert the scenario to an INI
	scenarioINI = []
	for cattitle, catcontents in scenario.iteritems():
		scenarioINI.append('[%s]' % cattitle)
		for key, value in catcontents.iteritems():
			scenarioINI.append('%s = %s' % (key, value))
	scenarioINI = '\n'.join(scenarioINI)

	log.info('Scenario INI:')
	log.info(scenarioINI)

	# Write scenario
	scenario_filename = os.path.join(pred_root, 'scenario')
	scenario_file = open(scenario_filename, 'w')
	scenario_file.write(scenarioINI + '\n')
	scenario_file.close()

	# Where is the prediction app?
	pred_app = '/societies/cuspaceflight/git/cusf-landing-prediction/pred'

	log.info('Launching prediction application...')

	# Try to wire everything up
	output_filename = os.path.join(pred_root, 'output')
	output_file = open(output_filename, 'w')
	pred_process = subprocess.Popen( \
		(pred_app, '-v', '-i', '/societies/cuspaceflight/landing-prediction-data/gfs', scenario_filename),
		stdout=output_file, stderr=log_file)
	pred_process.wait()
	if pred_process.returncode:
		raise RuntimeError('Prediction process %s returned error code: %s.' % (pred_uuid, pred_process.returncode))
	output_file.close()

	# Convert the output to a KML file
	output_to_kml(output_filename, os.path.join(pred_root, 'output.kml'))

	# Print the CGI header and prediction UUID.
	print "Content-Type: text/plain" 
	print "Status: 201 Created"
	print
	print pred_uuid

if __name__ == '__main__':
	main()
