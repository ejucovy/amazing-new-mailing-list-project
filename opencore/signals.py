from django.dispatch import Signal

user_activated = Signal(providing_args=['user'])
contact_confirmed = Signal(providing_args=['contact'])
