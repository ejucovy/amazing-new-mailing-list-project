from django.conf import settings
from django.utils.importlib import import_module

_subscription_policy_cache = {}
def get_subscription_policies():
    if _subscription_policy_cache:
        return dict(_subscription_policy_cache)

    policies = settings.LIST_SUBSCRIPTION_MODERATION_POLICIES
    for key, policy in policies:
        mod_name, klass_name = policy.rsplit('.', 1)
        mod = import_module(mod_name)
        klass = getattr(mod, klass_name)
        _subscription_policy_cache[key] = klass()
        
    return dict(_subscription_policy_cache)

def get_subscription_policy(key):
    return get_subscription_policies()[key]


_post_policy_cache = {}
def get_post_policies():
    if _post_policy_cache:
        return dict(_post_policy_cache)

    policies = settings.LIST_POST_MODERATION_POLICIES
    for key, policy in policies:
        mod_name, klass_name = policy.rsplit('.', 1)
        mod = import_module(mod_name)
        klass = getattr(mod, klass_name)
        _post_policy_cache[key] = klass()
        
    return dict(_post_policy_cache)

def get_post_policy(key):
    return get_post_policies()[key]
