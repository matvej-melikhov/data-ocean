from app import application, db
from app import models
from app import routes
from app.admin_views import *

with application.app_context():
    db.create_all()

if __name__ == "__main__":
    application.run(debug=True, port=5000)
