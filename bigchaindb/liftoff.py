from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import click
import yaml
from pprint import pprint
import calendar
import time

bdb_cfg = {}
config_file = None
bdb = None


@click.group()
@click.option('--config', help='configuration file.', default='liftoff.yml')
def cli(config):
  """ LIFTOFF interface to blockchain. """
  global bdb_cfg, config_file, bdb
  config_file = config
  bdb_cfg = yaml.load(open(config, 'r'))

  bdb = BigchainDB(
    bdb_cfg['bigchaindb']['url'],
    headers=bdb_cfg['headers'])


@cli.command()
@click.option('--name', help='name of the user.')
@click.option('--private-key', is_flag=True, help='show also private key.')
def user(name, private_key):
  """ Create/show user and it's keypairs """
  global bdb_cfg, config_file

  if name is not None:
    new_user = generate_keypair()

    bdb_cfg['user'] = {}
    bdb_cfg['user']['name'] = name
    bdb_cfg['user']['public_key'] = new_user.public_key
    bdb_cfg['user']['private_key'] = new_user.private_key
    yml_str = yaml.dump(bdb_cfg, width=80, indent=4, default_flow_style=False)
    with open (config_file, 'w') as f:
      f.write (yml_str)
    print ("configuration file '{}' updated.".format(config_file))
  else:
    show_keys = ['name', 'public_key']
    if private_key:
      show_keys.append('private_key')
    for key in show_keys:
      print ("{:>15s}: {}".format(key, bdb_cfg['user'][key]))


@cli.command()
@click.option('--obj', required=True, help='the object type name to create.')
@click.option('--obj-id', required=True, help='the object ID to create.')
def create(obj, obj_id):
  """ Create (CRAB) data in the bigchaindb. """
  global bdb_cfg, bdb

  now_epoch = calendar.timegm(time.gmtime())

  tu = {
    'data': {
      'index': '__liftoff__{app_key}__{obj}__{obj_id}'.format (app_key=bdb_cfg['headers']['app_key'], obj=obj, obj_id=obj_id),
      'object-type': obj,
      'object-id': obj_id,
      'tu': {
          'serial_number': 'QWERTY',
          'manufacturer': 'catan',
          'people_capacity': 4,
          'package_capacity': 2,
          'batery_capacity': 100,
      },
      'created_at': now_epoch,
    }
  }

  metadata = {
    'odo': 10,
    'lat': 53,
    'lon': 6.6,
    'batery_charge_level': 50,
    'state': 'idle',
  }

  tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=bdb_cfg['user']['public_key'],
    asset=tu,
    metadata=metadata)

  txid = tx['id']

  signed_tx = bdb.transactions.fulfill(
    tx,
    private_keys=bdb_cfg['user']['private_key'])

  bdb.transactions.send(signed_tx)
  print ("created asset {}".format (txid))


@cli.command()
@click.option('--query', help='query for the objects to read.', default='')
def read(query):
  """ Read (CRAB) data from the bigchaindb. """
  global bdb_cfg, bdb
  search_query = '__liftoff__'+bdb_cfg['headers']['app_key'] + ' ' + query
  search_query = query

  assets = bdb.assets.get(search=search_query)

  print ("results for query: '{}'".format (search_query))
  print ("--------------------{}-".format ('-' * len(search_query)))

  for asset in assets:
    asset_details = bdb.transactions.get(asset_id=asset['id'])
    print ("asset")
    print ("=====")
    print ("")
    first_time = True
    for ad in asset_details:
      pprint (">>>")
      print ('asset-id: {}'.format (ad['id']))
      first_time = False
      if 'data' in ad['asset']:
        print ("data:")
        pprint (ad['asset']['data'])
      if 'metadata' in ad:
        print ("metadata:")
        pprint (ad['metadata'])
      pprint ("<<<")


@cli.command()
@click.option('--odo', help='append odo to metadata.')
@click.option('--burn', is_flag=True, help='burn the entry in the database.')
def append(odo, burn):
  """ Append/Burn (CRAB) metadata to the bigchaindb. """
  global bdb_cfg, bdb

  now_epoch = calendar.timegm(time.gmtime())
  metadata = {'odo': odo,
              'appended_at': now_epoch }

  print ("todo: have the asset id as parameter??!")
  transfer_asset = {
    'id': '6cc7196870c2ac62a80d84f5059439f01d142e1b0e1ebbb9228d44c3a4b6eff8'
  }
  print ("asset_id: ", transfer_asset['id'])

  asset_details = bdb.transactions.get(asset_id=transfer_asset['id'])

  output_index = 0
  output = asset_details[0]['outputs'][output_index]
  transfer_input = {
    'fulfillment': output['condition']['details'],
    'fulfills': {
      'output_index': output_index,
      'transaction_id': asset_details[-1]['id'],
    },
    'owners_before': output['public_keys'],
  }

  private_key = bdb_cfg['user']['private_key']
  public_key = bdb_cfg['user']['public_key']
  if burn:
    lost_user = generate_keypair ()
    public_key = lost_user.public_key # and do not store the key of the lost_user....
    metadata = { 'burned_at': now_epoch }

  prepared_transfer_tx = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=public_key,
    metadata=metadata,
  )

  fulfilled_transfer_tx = bdb.transactions.fulfill(
    prepared_transfer_tx,
    private_keys=private_key,
  )

  sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)
  print (sent_transfer_tx == fulfilled_transfer_tx)


if __name__ == "__main__":
  cli()
