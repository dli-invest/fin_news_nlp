import uvicorn
import os
from app.api import app

if __name__ == '__main__':
    port = os.getenv('PORT', 8080)
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')