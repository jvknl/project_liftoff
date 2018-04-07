Bigchaindb: https://testnet.bigchaindb.com/login
Username: liftoff
Email: karel.vanroye@gmail.com
Password: 2Play@Catan
Docs: https://docs.bigchaindb.com/projects/py-driver
Blog: https://blog.bigchaindb.com/introducing-queryable-assets-in-bigchaindb-v-1-0-adbe1b86e622
CRAB:(javascript) https://tutorials.bigchaindb.com/crab/
Get started: https://www.bigchaindb.com/getstarted/


“Asset” has “data“ and “metadata”.
“Data” is immutable, non-appendable, and is available in the first transaction.
“Data” can be queried with text field
Query with exclude text field possible
Query with “Phrase” or exact match possible
Query with “oring” words is possible by a ‘space’.
Query with “anding” words is NOT possible!
“Metadata” is immutable, appendable, and can thus be updated very TRANSFER transaction.
Query is not possible on metadata.
“Queries” search the entire database
No concept of tables
Add ‘app_key’ to the field ⇒ our app can search our data.
No AND query with text field possible
Add ‘index’ parameter with our app-key, and the most often needed queries ⇒ we can search with “exact” match.
Results of queries can be limited (in amount), note: meta data is not ‘merged’.




asset-id: dc5c59ff2bfbda5cc4064543db579f4f10712201880234b1f9d1eb9b0677b967
data:
{'name': 'tu_for_append',
 'tu': {'batery_capacity': 100,
        'manufacturer': 'catan',
        'package_capacity': 2,
        'people_capacity': 4,
        'serial_number': 'tu_for_append'},
 'us': '__liftoff__323e58f2f88da58e4dba8f35c4699823'}
metadata:
{'batery_charge_level': 50, 'lat': 53, 'lon': 6.6, 'odo': 10, 'state': 'idle'}
'<<<'
⇒ here meta data is appended, only the metadata ‘odo’ was supplied
'>>>'
metadata:
{'odo': 111}
'<<<'
