"""Discord connector (real Discord HTTP API with a bot token).

Uses the Discord REST API via httpx. Only servers/channels the token can see are
reachable. Offline/mock mode returns deterministic simulated results.
"""
from __future__ import annotations

import base64
import io
from typing import Any

import httpx

from ..base import Connector, Op, Param
from ..errors import ApiError, NotConfigured

API = "https://discord.com/api/v10"


class DiscordConnector(Connector):
    platform = "discord"
    namespace = "discord"
    display_name = "Discord"

    OPS = {
        "list_servers": Op("list_servers", "List guilds the bot belongs to.", []),
        "list_channels": Op("list_channels", "List channels in a guild.", [
            Param("server_id", "str", False, "Guild id.")]),
        "list_messages": Op("list_messages", "Read recent messages in a channel.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("limit", "int", False, "Max.", 50)]),
        "search": Op("search", "Search message history for a term.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("query", "str", True, "Term."),
            Param("limit", "int", False, "Scan window.", 200)]),
        "send": Op("send", "Send a message to a channel.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("content", "str", True, "Message text.")], "discord.send", True),
        "reply": Op("reply", "Reply to a specific message.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("message_id", "str", True, "Message id."),
            Param("content", "str", True, "Reply text.")], "discord.send", True),
        "send_dm": Op("send_dm", "Open a DM and send a message to a user.", [
            Param("user_id", "str", True, "User id."),
            Param("content", "str", True, "Text.")], "discord.send", True),
        "send_file": Op("send_file", "Upload a file to a channel (base64 content).", [
            Param("channel_id", "str", True, "Channel id."),
            Param("filename", "str", True, "Filename."),
            Param("content_base64", "str", True, "Base64 file bytes."),
            Param("caption", "str", False, "Caption.")], "discord.send", True),
        "react": Op("react", "Add a reaction to a message.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("message_id", "str", True, "Message id."),
            Param("emoji", "str", True, "Emoji.")], "discord.send", True),
        "create_thread": Op("create_thread", "Create a thread from a message.", [
            Param("channel_id", "str", True, "Channel id."),
            Param("message_id", "str", True, "Message id."),
            Param("name", "str", True, "Thread name.")], "discord.send", True),
    }

    def configured(self) -> bool:
        return bool(self.settings.discord_token)

    def _headers(self):
        return {"Authorization": f"Bot {self.settings.discord_token}"}

    def _get(self, path, **params):
        r = httpx.get(f"{API}{path}", headers=self._headers(), params=params, timeout=30)
        if r.status_code >= 400:
            raise ApiError(f"discord GET {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def _post(self, path, payload):
        r = httpx.post(f"{API}{path}", headers=self._headers(), json=payload, timeout=30)
        if r.status_code >= 400:
            raise ApiError(f"discord POST {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def _require_live(self):
        if self._mock:
            raise NotConfigured("discord connector is mock/offline; set DISCORD_TOKEN "
                                "to operate live.")

    def op_list_servers(self, args, account):
        self._require_live()
        g = self._get("/users/@me/guilds")
        return {"servers": [{"id": x["id"], "name": x["name"]} for x in g]}

    def op_list_channels(self, args, account):
        self._require_live()
        gid = args.get("server_id")
        if not gid:
            gs = self.op_list_servers(args, account)["servers"]
            if not gs:
                return {"channels": []}
            gid = gs[0]["id"]
        ch = self._get(f"/guilds/{gid}/channels")
        return {"server_id": gid, "channels": [
            {"id": c["id"], "name": c["name"], "type": c["type"]} for c in ch]}

    def op_list_messages(self, args, account):
        self._require_live()
        ms = self._get(f"/channels/{args['channel_id']}/messages",
                       limit=min(int(args.get("limit", 50)), 100))
        return {"channel_id": args["channel_id"], "messages": [
            {"id": m["id"], "author": (m.get("author") or {}).get("username"),
             "content": m.get("content", ""), "timestamp": m.get("timestamp")}
            for m in ms]}

    def op_search(self, args, account):
        self._require_live()
        ms = self.op_list_messages({"channel_id": args["channel_id"],
                                    "limit": args.get("limit", 200)},
                                   account)["messages"]
        q = args["query"].lower()
        return {"matches": [m for m in ms if q in m["content"].lower()]}

    def op_send(self, args, account):
        self._require_live()
        r = self._post(f"/channels/{args['channel_id']}/messages",
                       {"content": args["content"]})
        return {"message_id": r.get("id"), "channel_id": args["channel_id"], "sent": True}

    def op_reply(self, args, account):
        self._require_live()
        r = self._post(f"/channels/{args['channel_id']}/messages",
                       {"content": args["content"],
                        "message_reference": {"message_id": args["message_id"]}})
        return {"message_id": r.get("id"), "replied_to": args["message_id"], "sent": True}

    def op_send_dm(self, args, account):
        self._require_live()
        ch = self._post("/users/@me/channels", {"recipient_id": args["user_id"]})
        r = self._post(f"/channels/{ch['id']}/messages", {"content": args["content"]})
        return {"message_id": r.get("id"), "user_id": args["user_id"], "sent": True}

    def op_send_file(self, args, account):
        self._require_live()
        data = base64.b64decode(args["content_base64"])
        files = {"file": (args["filename"], io.BytesIO(data))}
        payload = {"content": (None, args.get("caption") or "")}
        rr = httpx.post(f"{API}/channels/{args['channel_id']}/messages",
                        headers=self._headers(), data=payload, files=files, timeout=60)
        if rr.status_code >= 400:
            raise ApiError(f"discord upload -> {rr.status_code}: {rr.text[:300]}")
        j = rr.json()
        return {"message_id": j.get("id"), "filename": args["filename"], "uploaded": True}

    def op_react(self, args, account):
        self._require_live()
        import urllib.parse
        e = urllib.parse.quote(args["emoji"])
        r = httpx.put(f"{API}/channels/{args['channel_id']}/messages/"
                      f"{args['message_id']}/reactions/{e}/@me",
                      headers=self._headers(), timeout=30)
        if r.status_code >= 400:
            raise ApiError(f"discord react -> {r.status_code}: {r.text[:200]}")
        return {"reacted": True, "emoji": args["emoji"]}

    def op_create_thread(self, args, account):
        self._require_live()
        r = self._post(f"/channels/{args['channel_id']}/messages/"
                       f"{args['message_id']}/threads",
                       {"name": args["name"]})
        return {"thread_id": r.get("id"), "created": True}
