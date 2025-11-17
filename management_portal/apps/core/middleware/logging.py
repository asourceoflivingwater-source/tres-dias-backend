import logging 

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter =  logging.Formatter(fmt='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s')
handler.formatter = formatter
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        request_data = {
            'method': request.method,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'path': request.path
        }

        logger.info(request_data)
        
        response = self.get_response(request)
        
        response_dict = {
                    'status': response.status_code
                }
        logger.info(response_dict)
        
        return response