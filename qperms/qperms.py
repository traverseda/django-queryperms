import rules
from threadlocals.threadlocals import get_current_request
from django.db import models
from django.db.models import Q, FilteredRelation

class QpermQueryset(models.QuerySet):
    """A Queryset that supports qperm permissions"""
    def perms(self,perms,user=None):
        if not user:
            user=get_current_request().user
        if user.is_superuser:
            return self
        perms=perms.split("|")
        q=Q()
        for perm in perms:
            q=q|getattr(self.model,"qperms_"+perm)(user)
        return self.filter(q)

def qperm_related_perms(obj,related_name,perm_name):
    """ Use this to apply another object's perms to your object...
    """
    try:
        related_obj = getattr(obj, related_name)
    except AttributeError:
        raise AttributeError(
            "QueryPerms can't find related foreign key `{}` on `{}`".format(
                obj.related_name, obj
            )
        )
    related_allowed=related_obj.objects.perms(perm_name)
    return Q(**{related_name+'__in'):related_allowed})

class QpermMixin:
    qperms_parent = None
    objects = QpermQueryset.as_manager()

    def qperm_view(self):
        if qperms_parent:
            return qperm_related_perms(self,qperms_parent,"view")
        return Q()

    def qperm_edit(self):
        if qperms_parent:
            return qperm_related_perms(self,qperms_parent,"edit")
        return Q()

    def qperm_delete(self):
        if qperms_parent:
            return qperm_related_perms(self,qperms_parent,"delete")
        return self.qperm_edit()

@rules.predicate
def is_superuser(user):
    return user.is_superuser

def remove_prefix(text, prefix):
    #ToDo: Not needed in python3.9, where strings can just do this
    if text.startswith(prefix):
        return text[len(prefix):]
    return text # or whatever

def qperms_register(model):
    methods = [
        method_name
        for method_name in dir(model)
        if callable(getattr(model, method_name)) and method_name.startswith("qperm_")
    ]
    methods = {
        remove_prefix(method_name, "qperm_"): getattr(model, method_name)
        for method_name in methods
    }

    app_name = model._meta.app_label
    model_name = model._meta.model_name
    rules.add_perm(f"{app_name}.{model_name}", rules.always_allow)
    rules.add_perm(f"{app_name}.view_{model_name}", rules.always_allow)
    rules.add_perm(f"{app_name}.add_{model_name}", rules.always_allow)
    for method_name, method in methods.items():
        model_name = model._meta.model_name
        rulename = f"{app_name}.{method_name}_{model_name}"

        @rules.predicate
        def queryChecker(model):
            if model:
                return (
                    model.__class__.objects.filter(method())
                    .filter(id=model.id)
                    .exists()
                )
            # We don't care about generic object listings, those need to be filtered
            # using the qpermadmin mixin.
            return True

        rules.add_perm(rulename, is_superuser | queryChecker)

from django.db.models.signals import class_prepared

def handle_prepared(sender):
    if issubclass(sender,QpermMixin):
        qperms_register(sender)

class_prepared.connect(handle_prepared)
