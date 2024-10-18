from app import application
from app import models
from app import routes
from app.admin_views import *

if __name__ == "__main__":
    application.run(port=8000, debug=True)