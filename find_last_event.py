import datetime
import pymongo
import json
from bottle import route, post, get, run, template, static_file, request, app, HTTPError, abort, BaseRequest, JSONPlugin, response
from dateutil.parser import parse
# To support dynamic loading of client-specific libraries
import socket
import fake_mongo_types as clsrfmt
import requests

BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024 # Allow the request size to be 1G
# to accomodate large section sizes

app = app()

def get_last_event_from_server(upload_address, date):
    day_start = date.isoformat()
    day_end = (date + datetime.timedelta(days=1)).replace(hour=0, minute=0, 
            second=0, microsecond=0).isoformat()
    query = {"data.end_time": {"$lt": day_end, "$gt": day_start}}
    filters = {"_id": False}
    db = clsrfmt.CalendarCollection(upload_address)
    data = list(db.find(query, filters).sort('data.end_time', pymongo.DESCENDING))
    if len(data) == 0:
        return None
    else:
        return data[0]

@post("/get_last_event")
def get_arrival_time():
    upload_address = request.json['pm_address']
    # Extract the date and round down
    date = parse(request.json['date'])
    last_event = get_last_event_from_server(upload_address, date)
    if last_event is None:
        return None
    else:
        end_time = last_event['data']['end_time']
        location = last_event['data']['geo']
        return {'time' : end_time, 'geo': location}

if __name__ == '__main__':
    # To avoid config file for tests
    server_host = socket.gethostbyname(socket.gethostname())

    upc_port = 80

    # The selection of SSL versus non-SSL should really be done through a config
    # option and not through editing source code, so let's make this keyed off the
    # port number
    if upc_port == 443:
      # We support SSL and want to use it
      try:
        key_file = open('conf/net/keys.json')
      except:
        key_file = open('conf/net/keys.json.sample')
      key_data = json.load(key_file)
      host_cert = key_data["host_certificate"]
      chain_cert = key_data["chain_certificate"]
      private_key = key_data["private_key"]

      run(host=server_host, port=upc_port, server='cheroot', debug=True,
          certfile=host_cert, chainfile=chain_cert, keyfile=private_key)
    else:
      # Non SSL option for testing on localhost
      print("Running with HTTPS turned OFF - use a reverse proxy on production")
      run(host=server_host, port=upc_port, server='cheroot', debug=True)

    # run(host="0.0.0.0", port=server_port, server='cherrypy', debug=True)
