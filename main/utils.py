
def requires(permissions):
    if isinstance(permissions, basestring):
        permissions = [permissions]
    def wrapper(func):
        def inner(request, *args, **kw):
            available_permissions = request.list.get_permissions(request)
            for permission in permissions:
                if permission not in available_permissions:
                    return HttpResponseForbidden()
            return func(request, *args, **kw)
        return inner
    return wrapper
