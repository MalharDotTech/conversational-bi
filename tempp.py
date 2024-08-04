from vanna.remote import VannaDefault
vn = VannaDefault(model='sales_model', api_key='b400ee9447fe46b9a41175fc3bf18bf1')
vn.connect_to_sqlite("./sales_db.sqlite")

from vanna.flask import VannaFlaskApp
VannaFlaskApp(vn,allow_llm_to_see_data=True).run()
