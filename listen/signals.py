from django.dispatch import Signal

post_submitted = Signal(providing_args=['post', 'author', 'subject', 'body'])
post_rejected = Signal(providing_args=['post', 'author', 'subject', 'body'])
post_accepted = Signal(providing_args=['post', 'author', 'subject', 'body'])

subscription_submitted = Signal(providing_args=['user', 'list'])
subscription_rejected = Signal(providing_args=['user', 'list'])
subscription_accepted = Signal(providing_args=['user', 'list'])
