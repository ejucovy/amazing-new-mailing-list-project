"""
Implements a set of Post Moderation Policy components that can be used in mailing lists
for various workflows.  In order to be active a policy must be referenced by dottedname in the 
``settings.LIST_POST_MODERATION_POLICIES`` tuple.
"""

from django.contrib import messages
from main.models import LocalRoles, MailingListPost

class BasePolicy(object):

    def accept_post(self, list, author, subject, body):
        post = MailingListPost.objects.create(list=list, author=author,
                                              subject=subject, body=body)
        post.save()
        return post        

    def flag_post(self, list, author, subject, body):
        post = MailingListPost.objects.create(list=list, author=author,
                                              subject=subject, body=body,
                                              flagged=True)
        post.save()
        return post                

    def process_request(self, list, author, subject, body):
        permissions = list.get_permissions(author)
        if "LIST_POST" in permissions:
            return (True, self.accept_post(list, author, subject, body),
                    messages.SUCCESS, "Your message has been posted.")
        raise NotImplementedError

class OpenPolicy(BasePolicy):

    description = "Automatically accept all posts from senders who have confirmed their contact information"

    def process_request(self, list, author, subject, body):
        try:
            return BasePolicy.process_request(self, list, author, subject, body)
        except NotImplementedError:
            return (True, self.accept_post(list, author, subject, body),
                    messages.SUCCESS, "Your message has been posted.")


class MediumPolicy(BasePolicy):

    description = "Moderate posts that are not from explicitly allowed senders"

    def process_request(self, list, author, subject, body):
        try:
            return BasePolicy.process_request(self, list, author, subject, body)
        except NotImplementedError:
            return (False, self.flag_post(list, author, subject, body),
                    messages.INFO, "Your message has been submitted for moderation by the censors.")


class ClosedPolicy(BasePolicy):

    description = "Reject all posts that are not from explicitly allowed senders"

    def process_request(self, list, author, subject, body):
        try:
            return BasePolicy.process_request(self, list, author, subject, body)
        except NotImplementedError:
            return (False, None,
                    messages.ERROR, "This list does not allow unsolicited messages.")
