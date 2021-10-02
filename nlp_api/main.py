import uvicorn
import os
from app.api import app


if __name__ == '__main__':
    port = os.getenv('PORT', 8080)
    # try:
    #     from waitress import serve
    #     serve(app, host='0.0.0.0', port=port)
    # except ImportError as e:
    #     print(e)
    #     app.run(host='0.0.0.0', debug=True)
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')