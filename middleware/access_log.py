import time
import logging

logger = logging.getLogger('access')

class AccessLogger:
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        end = time.time()
        
        duration = round((time.time() - start) * 1000, 2)
        user = request.user.username if request.user.is_authenticated else "Anon"
        
        logger.info(f"{request.method} {request.path}"
                    f" {response.status_code} {duration}ms"
                    f" User: {user}")
        
        return response