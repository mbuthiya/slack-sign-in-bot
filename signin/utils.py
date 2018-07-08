def get_client_ip(request):
    ip = request.META.get('REMOTE_ADDR')
    return ip
