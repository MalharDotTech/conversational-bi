from vanna.remote import VannaDefault
vn = VannaDefault(model='ibm_acc', api_key='b400ee9447fe46b9a41175fc3bf18bf1')
vn.connect_to_sqlite("./ibm_acc.database.sqlite")

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn).run()
