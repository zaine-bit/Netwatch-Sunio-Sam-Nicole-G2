from functools import wraps
from django.shortcuts import redirect
from .models import Account


def account_login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        account_id = request.session.get("account_id")
        if not account_id:
            return redirect("accounts:login")
        try:
            request.account = Account.objects.get(pk=account_id, is_active=True)
        except Account.DoesNotExist:
            request.session.flush()
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return wrapped
