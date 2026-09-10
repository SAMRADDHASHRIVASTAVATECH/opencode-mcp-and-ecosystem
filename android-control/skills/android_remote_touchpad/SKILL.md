# android_remote_touchpad

Manage the vendored remote-touchpad host (phone-as-PC-input companion). This is the reverse-direction capability: an authorized Android phone's browser controls THIS Windows PC's pointer and keyboard over the LAN. actions: status | start | stop | resolve. Requires AC_RT_ENABLED=true and a real remote-touchpad binary (see AC_RT_BIN / downloader script).

- kind: `remote-touchpad`
- callable: ``android_control.skills.android_remote_touchpad``
- master orchestrates: ``android_control``
