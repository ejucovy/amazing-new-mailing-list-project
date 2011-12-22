"""
Implements a set of Subscription Moderation Policy components that can be used in mailing lists
for various workflows.  In order to be active a policy must be referenced by dottedname in the 
``settings.LIST_SUBSCRIPTION_MODERATION_POLICIES`` tuple.
"""

from django.contrib import messages
from main.models import LocalRoles

class OpenPolicy(object):

    description = "Automatically accept all subscription requests"

    def process_request(self, list, user):
        user_roles, _ = LocalRoles.objects.get_or_create(
            username=user.username, list=list)
        if user_roles.has_role("ListSubscriber"):
            return (False, None, messages.WARNING,
                    "You are already subscribed to this list!")

        user_roles.add_role("ListSubscriber")
        return (True, None, messages.SUCCESS,
                "Congratulations, you're now subscribed!")


class MediumPolicy(object):

    description = "Moderate subscription requests"

    def process_request(self, list, user):
        from main.models import SubscriptionQueue, LocalRoles

        user_roles, _ = LocalRoles.objects.get_or_create(
            username=user.username, list=list)
        if user_roles.has_role("ListSubscriber"):
            return (False, None, messages.WARNING,
                    "You are already subscribed to this list!")
        
        queue, created = SubscriptionQueue.objects.get_or_create(
            user=user,
            list=list,
            )
        queue.save()
        if created:
            return (False, queue, messages.INFO,
                    "Your request for moderation has been submitted to senior management.")
        else:
            return (False, queue, messages.WARNING,
                    "You already have a subscription request pending moderation.")

class ClosedPolicy(object):

    description = "Reject subscription requests"

    def process_request(self, list, user):
        user_roles, _ = LocalRoles.objects.get_or_create(
            username=user.username, list=list)
        if user_roles.has_role("ListSubscriber"):
            return (False, None, messages.WARNING,
                    "You are already subscribed to this list!")

        return (False, None, messages.ERROR,
                "This list does not allow new subscriptions.")

