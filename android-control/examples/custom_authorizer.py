#!/usr/bin/env python3
"""How to install an authorization policy so destructive operations can run.

By default destructive ops (uninstall / clear data / disable / overwrite)
RAISE RequiresAuthorizationError. Provide an authorizer to allow them under
your own policy. Run offline for a deterministic demo.
"""
import os
os.environ["AC_OFFLINE"] = "1"

from android_control.controller import AndroidControl
from android_control.high import AndroidFacade
from android_control.errors import RequiresAuthorizationError


def policy(op: str, detail: str) -> bool:
    # Example: only ever allow clearing OUR OWN test app, nothing else.
    if op == "clear" and "com.mycompany.testapp" in detail:
        print(f"[policy] ALLOW  {op}: {detail}")
        return True
    print(f"[policy] DENY   {op}: {detail}")
    return False


def main():
    ctrl = AndroidControl(offline=True, authorizer=policy)
    f = AndroidFacade(ctrl, autorun=False)
    ctrl.discover()
    serial = f.ctrl.registry.all()[0].serial

    # Allowed by policy:
    print("clear testapp ->",
          _try(lambda: ctrl.apps.clear_data(serial, "com.mycompany.testapp")))

    # Denied by policy -> RequiresAuthorizationError
    print("clear whatsapp ->",
          _try(lambda: ctrl.apps.clear_data(serial, "com.whatsapp")))

    # No authorizer at all -> default deny
    ctrl2 = AndroidControl(offline=True)
    ctrl2.discover()
    s2 = ctrl2.registry.all()[0].serial
    print("uninstall (no policy) ->",
          _try(lambda: ctrl2.apps.uninstall(s2, "com.whatsapp")))


def _try(fn):
    try:
        fn()
        return "ok"
    except RequiresAuthorizationError as e:
        return f"RequiresAuthorizationError: {e}"
    except Exception as e:  # noqa: BLE001
        return f"{type(e).__name__}: {e}"


if __name__ == "__main__":
    main()
