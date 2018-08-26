from typing import Dict, List

from repomate_plug import hookspec
from repomate_plug import exception

_HOOK_METHODS = {
    key: value
    for key, value in hookspec.CloneHook.__dict__.items()
    if callable(value) and not key.startswith('_')
}


class _PluginMeta(type):
    """Metaclass used for converting methods with appropriate names into
    hook methods.

    Also ensures that all public methods have the name of a hook method.

    Checking signatures is handled by pluggy on registration.
    """

    def __new__(cls, name, bases, attrdict):
        """Check that all public methods have hook names, convert to hook
        methods and return a new instance of the class. If there are any
        public methods that have non-hook names,
        :py:function:`repomate_plug.exception.HookNameError` is raised.

        Checking signatures is delegated to ``pluggy`` during registration of
        the hook.
        """
        print("processing {}".format(name))
        methods = cls._extract_public_methods(attrdict)
        cls._check_names(methods)
        hooked_methods = {
            name: hookspec.hookimpl(method)
            for name, method in methods.items()
        }
        attrdict.update(hooked_methods)

        return super().__new__(cls, name, bases, attrdict)

    @staticmethod
    def _check_names(methods):
        hook_names = set(_HOOK_METHODS.keys())
        method_names = set(methods.keys())
        if not method_names.issubset(hook_names):
            raise exception.HookNameError(
                "public method(s) with non-hook name: {}".format(
                    ", ".join(method_names - hook_names)))

    @staticmethod
    def _extract_public_methods(attrdict):
        return {
            key: value
            for key, value in attrdict.items()
            if callable(value) and not key.startswith('_')
        }


class Plugin(metaclass=_PluginMeta):
    """Base class for plugin classes. For plugin classes to be picked up by
    ``repomate``, they must inherit from this class.

    Public methods must be hook methods, i.e. implement the specification of
    one of the hooks defined in :py:class:`repomate_plug.hookspec.CloneHook`.
    If there are any other public methods, an error is raised on class
    creation. As long as the method has the correct name, it will be recognized
    as a hook method.

    The signature of the method is not checked until the hook is registered by
    the :py:constant:`repomate_plug.manager` (an instance of
    :py:class:`pluggy.manager.PluginManager`). Therefore, when testing a plugin,
    it is a good idea to include a test where it is registered with the manager
    to ensure that it has the correct signatures.

    Private methods (i.e. methods prefixed with ``_``) carry no such
    restrictions.
    """