"""Google Workspace connector (real official Google APIs).

Authentication supports a service account (GOOGLE_APPLICATION_CREDENTIALS) or
installed-app OAuth (GOOGLE_CLIENT_SECRETS + token at GOOGLE_TOKEN_PATH).
Handlers call the real APIs. When unconfigured (or UNIFIED_OFFLINE=1) the
connector reports mock mode and returns deterministic simulated results so the
engines/tests run; real mode is authoritative. Nothing is faked in live mode.
"""
from __future__ import annotations

import base64
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Any, Dict

from ..base import Connector, Op, Param
from ..errors import AuthError, NotConfigured, NotSupported, Validation


class GoogleConnector(Connector):
    platform = "google"
    namespace = "google"
    display_name = "Google Workspace"
    OPS = {
        # ---- Gmail ----
        "gmail.search": Op("gmail.search", "Search Gmail using Gmail search operators "
                           "(query, optional maxResults).", [
            Param("query", "str", True, "Gmail search query, e.g. 'from:client subject:contract'"),
            Param("maxResults", "int", False, "Max results.", 25),
            Param("labelIds", "list", False, "Labels.")], "google.gmail.read"),
        "gmail.read": Op("gmail.read", "Read a single email by id (returns body, "
                         "headers, snippet).", [
            Param("id", "str", True, "Gmail message id.")], "google.gmail.read"),
        "gmail.read_thread": Op("gmail.read_thread", "Read a full thread by thread id.",
                                [Param("id", "str", True, "Gmail thread id.")], "google.gmail.read"),
        "gmail.send": Op("gmail.send", "Send an email.", [
            Param("to", "str", True, "Recipient(s), comma separated."),
            Param("subject", "str", True, "Subject."),
            Param("body", "str", True, "Body."),
            Param("cc", "str", False, "CC recipients."),
            Param("bcc", "str", False, "BCC recipients."),
            Param("html", "bool", False, "Treat body as HTML.")], "google.gmail.send", True),
        "gmail.reply": Op("gmail.reply", "Reply to an existing email, preserving "
                          "thread context.", [
            Param("id", "str", True, "Original message id."),
            Param("body", "str", True, "Reply body."),
            Param("to_override", "str", False, "Optional explicit recipient.")],
            "google.gmail.send", True),
        "gmail.forward": Op("gmail.forward", "Forward an existing email.", [
            Param("id", "str", True, "Message id."), Param("to", "str", True, "Recipient.")],
            "google.gmail.send", True),
        "gmail.draft": Op("gmail.draft", "Create a draft.", [
            Param("to", "str", True, "Recipient."), Param("subject", "str", True, "Subject."),
            Param("body", "str", True, "Body.")], "google.gmail.send"),
        "gmail.labels": Op("gmail.labels", "Apply/remove labels on a message.", [
            Param("id", "str", True, "Message id."), Param("add", "list", False, "Labels to add."),
            Param("remove", "list", False, "Labels to remove.")], "google.gmail.modify", True),
        "gmail.trash": Op("gmail.trash", "Trash (archive) a message.", [
            Param("id", "str", True, "Message id.")], "google.gmail.modify", True),
        # ---- Calendar ----
        "calendar.list": Op("calendar.list", "List calendar events in a time window.", [
            Param("calendarId", "str", False, "Calendar id (default 'primary').", "primary"),
            Param("timeMin", "str", False, "ISO start."),
            Param("timeMax", "str", False, "ISO end."),
            Param("maxResults", "int", False, "Max results.", 50)], "google.calendar.read"),
        "calendar.search": Op("calendar.search", "Search events by free-text query.", [
            Param("q", "str", True, "Query."), Param("maxResults", "int", False, "Max.", 25)],
            "google.calendar.read"),
        "calendar.create": Op("calendar.create", "Create a calendar event.", [
            Param("summary", "str", True, "Title."), Param("start", "str", True, "Start ISO."),
            Param("end", "str", True, "End ISO."),
            Param("attendees", "list", False, "Attendee emails."),
            Param("description", "str", False, "Description."),
            Param("location", "str", False, "Location/meet."),
            Param("calendarId", "str", False, "Calendar.", "primary")],
            "google.calendar.write", True),
        "calendar.update": Op("calendar.update", "Update an event (fields present).", [
            Param("eventId", "str", True, "Event id."),
            Param("calendarId", "str", False, "Calendar.", "primary"),
            Param("summary", "str", False, "New title."),
            Param("start", "str", False, "New start ISO."),
            Param("end", "str", False, "New end ISO."),
            Param("attendees", "list", False, "Attendee emails."),
            Param("description", "str", False, "Description.")], "google.calendar.write", True),
        "calendar.cancel": Op("calendar.cancel", "Cancel/delete an event.", [
            Param("eventId", "str", True, "Event id."),
            Param("calendarId", "str", False, "Calendar.", "primary")],
            "google.calendar.write", True, destructive=True),
        "calendar.availability": Op("calendar.availability", "Find free slots in a window.", [
            Param("timeMin", "str", True, "Start ISO."), Param("timeMax", "str", True, "End ISO."),
            Param("durationMin", "int", False, "Slot duration minutes.", 30),
            Param("calendarId", "str", False, "Busy calendar.", "primary")], "google.calendar.read"),
        # ---- Drive ----
        "drive.search": Op("drive.search", "Search Drive files by name/type/query.", [
            Param("query", "str", False, "Google Drive query (optional)."),
            Param("name", "str", False, "Filename filter."),
            Param("mimeType", "str", False, "e.g. application/vnd.google-apps.document"),
            Param("maxResults", "int", False, "Max.", 50)], "google.drive.read"),
        "drive.read": Op("drive.read", "Read file metadata + text (exported for docs/sheets).", [
            Param("fileId", "str", True, "File id.")], "google.drive.read"),
        "drive.download": Op("drive.download", "Download file bytes (base64) when permitted.", [
            Param("fileId", "str", True, "File id.")], "google.drive.read"),
        # ---- Docs / Sheets via Drive-level ops ----
        "docs.create": Op("docs.create", "Create a new Google Doc from content.", [
            Param("title", "str", True, "Doc title."), Param("content", "str", False, "Initial text."),
            Param("folderId", "str", False, "Parent folder.")], "google.docs.write", True),
        "docs.read": Op("docs.read", "Read a Google Doc as plain text.", [
            Param("fileId", "str", True, "Doc file id.")], "google.docs.read"),
        "sheets.read": Op("sheets.read", "Read a spreadsheet range.", [
            Param("spreadsheetId", "str", True, "Spreadsheet id."),
            Param("range", "str", True, "e.g. 'Sheet1!A1:C10'.")], "google.sheets.read"),
        "sheets.search": Op("sheets.search", "Search cells for a term across a range.", [
            Param("spreadsheetId", "str", True, "Spreadsheet id."),
            Param("range", "str", True, "Range."), Param("term", "str", True, "Search term.")],
            "google.sheets.read"),
        "sheets.write": Op("sheets.write", "Write values to a range.", [
            Param("spreadsheetId", "str", True, "Spreadsheet id."),
            Param("range", "str", True, "Range."),
            Param("values", "json", True, "2D array of values.")], "google.sheets.write", True),
        "sheets.append": Op("sheets.append", "Append a row.", [
            Param("spreadsheetId", "str", True, "Spreadsheet id."),
            Param("range", "str", True, "Target e.g. 'Sheet1!A1'."),
            Param("values", "json", True, "Row array.")], "google.sheets.write", True),
        # ---- Contacts (People API) ----
        "contacts.search": Op("contacts.search", "Search Google contacts (People API).", [
            Param("query", "str", True, "Name or email."), Param("pageSize", "int", False, "Max.", 20)],
            "google.contacts.read"),
        "contacts.resolve": Op("contacts.resolve", "Resolve a name to a unique contact; if "
                               "ambiguous returns candidates for confirmation.", [
            Param("name", "str", True, "Person/name to resolve.")], "google.contacts.read"),
        # ---- Tasks ----
        "tasks.create": Op("tasks.create", "Create a Google Task.", [
            Param("title", "str", True, "Task title."),
            Param("due", "str", False, "Due (ISO or 'yyyy-MM-dd')."),
            Param("notes", "str", False, "Notes.")], "google.tasks.write", True),
        "tasks.list": Op("tasks.list", "List Google Tasks.", [
            Param("maxResults", "int", False, "Max.", 100)], "google.tasks.read"),
        "tasks.complete": Op("tasks.complete", "Mark a task complete.", [
            Param("taskId", "str", True, "Task id.")], "google.tasks.write", True),
        "tasks.delete": Op("tasks.delete", "Delete a task.", [
            Param("taskId", "str", True, "Task id.")], "google.tasks.write", True, True),
        # ---- Google Chat ----
        "chat.send": Op("chat.send", "Send a message to a Chat space/thread.", [
            Param("space", "str", True, "Space resource name (e.g. 'spaces/AAAA')."),
            Param("text", "str", True, "Message text.")], "google.chat.send", True),
    }

    # ---- auth -------------------------------------------------------- #
    def configured(self) -> bool:
        return bool(self.settings.google_creds_path or self.settings.google_client_secrets)

    def _creds(self):
        import json
        from pathlib import Path
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
        except Exception as e:  # pragma: no cover
            raise AuthError(f"google-auth not installed: {e}")
        scopes = (self.settings.google_scopes or
                  "https://www.googleapis.com/auth/gmail.modify "
                  "https://www.googleapis.com/auth/calendar "
                  "https://www.googleapis.com/auth/drive "
                  "https://www.googleapis.com/auth/documents "
                  "https://www.googleapis.com/auth/spreadsheets "
                  "https://www.googleapis.com/auth/contacts "
                  "https://www.googleapis.com/auth/tasks "
                  "https://www.googleapis.com/auth/chat.messages").split()
        if self.settings.google_creds_path:
            try:
                return service_account.Credentials.from_service_account_file(
                    self.settings.google_creds_path, scopes=scopes)
            except Exception as e:
                raise AuthError(f"bad service account creds: {e}")
        # OAuth installed app
        cp = Path(self.settings.google_token_path).expanduser()
        if cp.exists():
            creds = Credentials.from_authorized_user_file(str(cp), scopes)
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    raise AuthError("OAuth token expired and could not refresh; "
                                    f"re-run oauth setup. ({e})")
            return creds
        raise AuthError(
            "No Google token found. Run `python -m unified.oauth google` on a host "
            "with a browser to create " + str(cp))

    def _svc(self, name, version):
        try:
            from googleapiclient.discovery import build
        except Exception as e:
            raise AuthError(f"google-api-python-client not installed: {e}")
        return build(name, version, credentials=self._creds(), cache_discovery=False)

    def _require_live(self):
        if self._mock:
            raise NotConfigured("google connector in mock/offline mode; set live "
                                "credentials to operate for real.")

    # ---- Gmail -------------------------------------------------------- #
    def op_gmail_search(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        res = svc.users().messages().list(userId="me", q=args.get("query"),
                                          maxResults=args.get("maxResults", 25),
                                          labelIds=args.get("labelIds")).execute()
        return {"messages": res.get("messages", []), "nextPageToken": res.get("nextPageToken")}

    def _msg_text(self, msg):
        parts = []
        payload = msg.get("payload", {})
        if payload.get("body", {}).get("data"):
            parts.append(base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "replace"))
        for part in payload.get("parts", []):
            if part.get("mimeType", "").startswith("text/") and part.get("body", {}).get("data"):
                parts.append(base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", "replace"))
        return "\n".join(parts)

    def op_gmail_read(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        m = svc.users().messages().get(userId="me", id=args["id"], format="full").execute()
        hdrs = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        return {"id": m["id"], "threadId": m.get("threadId"), "subject": hdrs.get("Subject"),
                "from": hdrs.get("From"), "to": hdrs.get("To"), "date": hdrs.get("Date"),
                "snippet": m.get("snippet"), "labelIds": m.get("labelIds"),
                "body": self._msg_text(m)[:30000]}

    def op_gmail_read_thread(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        t = svc.users().threads().get(userId="me", id=args["id"]).execute()
        msgs = [self.op_gmail_read({"id": x["id"]}, account) for x in t.get("messages", [])]
        return {"threadId": args["id"], "messages": msgs}

    def _encode_message(self, to, subject, body, cc=None, bcc=None, html=False,
                        reply_to=None):
        m = EmailMessage()
        m["To"] = to
        if cc: m["Cc"] = cc
        if bcc: m["Bcc"] = bcc
        m["Subject"] = subject
        if reply_to:
            for k in ("In-Reply-To", "References"):
                m[k] = f"<{reply_to}>"
        m.set_content(body)
        raw = m.as_bytes()
        return base64.urlsafe_b64encode(raw).decode()

    def op_gmail_send(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        raw = self._encode_message(args["to"], args["subject"], args["body"],
                                   args.get("cc"), args.get("bcc"), bool(args.get("html")))
        res = svc.users().messages().send(userId="me",
                                          body={"raw": raw}).execute()
        return {"id": res["id"], "threadId": res.get("threadId"), "sent": True,
                "to": args["to"], "subject": args["subject"]}

    def _original(self, svc, mid):
        m = svc.users().messages().get(userId="me", id=mid, format="metadata",
                                       metadataHeaders=["Subject", "From", "To", "Message-ID"]).execute()
        hdrs = {h["name"].lower(): h["value"] for h in m.get("payload", {}).get("headers", [])}
        return hdrs, m.get("threadId")

    def op_gmail_reply(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        hdrs, tid = self._original(svc, args["id"])
        to = args.get("to_override") or parseaddr(hdrs.get("from", ""))[1]
        subject = hdrs.get("subject", "")
        if not subject.lower().startswith("re:"):
            subject = "Re: " + subject
        raw = self._encode_message(to, subject, args["body"],
                                   reply_to=hdrs.get("message-id"))
        res = svc.users().messages().send(userId="me", body={
            "raw": raw, "threadId": tid}).execute()
        return {"id": res["id"], "threadId": tid, "replyTo": to, "subject": subject}

    def op_gmail_forward(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        hdrs, _ = self._original(svc, args["id"])
        subject = "Fwd: " + hdrs.get("subject", "").replace("Fwd: ", "")
        body = self.op_gmail_read({"id": args["id"]}, account)["body"]
        raw = self._encode_message(args["to"], subject,
                                   "---------- Forwarded message ----------\n" + body)
        res = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"id": res["id"], "forwardedTo": args["to"]}

    def op_gmail_draft(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        raw = self._encode_message(args["to"], args["subject"], args["body"])
        res = svc.users().drafts().create(userId="me",
                                          body={"message": {"raw": raw}}).execute()
        return {"draftId": res.get("id"), "messageId": res.get("message", {}).get("id")}

    def op_gmail_labels(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        out = {}
        for lab in (args.get("add") or []):
            r = svc.users().messages().modify(userId="me", id=args["id"],
                                              body={"addLabelIds": [lab]}).execute()
            out["added"] = r.get("labelIds")
        for lab in (args.get("remove") or []):
            r = svc.users().messages().modify(userId="me", id=args["id"],
                                              body={"removeLabelIds": [lab]}).execute()
            out["removed"] = r.get("labelIds")
        return out

    def op_gmail_trash(self, args, account):
        self._require_live()
        svc = self._svc("gmail", "v1")
        svc.users().messages().trash(userId="me", id=args["id"]).execute()
        return {"trashed": True, "id": args["id"]}

    # ---- Calendar ----------------------------------------------------- #
    def op_calendar_list(self, args, account):
        self._require_live()
        svc = self._svc("calendar", "v3")
        kw = {"calendarId": args.get("calendarId", "primary"),
              "maxResults": args.get("maxResults", 50)}
        if args.get("timeMin"): kw["timeMin"] = args["timeMin"]
        if args.get("timeMax"): kw["timeMax"] = args["timeMax"]
        res = svc.events().list(**kw).execute()
        return {"items": res.get("items", [])}

    def op_calendar_search(self, args, account):
        self._require_live()
        svc = self._svc("calendar", "v3")
        res = svc.events().list(calendarId="primary", q=args["q"],
                                maxResults=args.get("maxResults", 25)).execute()
        return {"items": res.get("items", [])}

    def _event_body(self, args):
        body = {"summary": args["summary"], "start": {"dateTime": args["start"]},
                "end": {"dateTime": args["end"]}}
        if args.get("description"): body["description"] = args["description"]
        if args.get("location"): body["location"] = args["location"]
        if args.get("attendees"):
            body["attendees"] = [{"email": a} for a in args["attendees"]
                                 if "@" in (a or "")]
        return body

    def op_calendar_create(self, args, account):
        self._require_live()
        svc = self._svc("calendar", "v3")
        ev = svc.events().insert(calendarId=args.get("calendarId", "primary"),
                                 body=self._event_body(args), conferenceDataVersion=1,
                                 sendUpdates="all").execute()
        return {"eventId": ev.get("id"), "htmlLink": ev.get("htmlLink"),
                "hangoutLink": ev.get("hangoutLink")}

    def op_calendar_update(self, args, account):
        self._require_live()
        svc = self._svc("calendar", "v3")
        cid = args.get("calendarId", "primary")
        ev = svc.events().get(calendarId=cid, eventId=args["eventId"]).execute()
        for k in ("summary", "description"):
            if args.get(k): ev[k] = args[k]
        if args.get("start"): ev["start"] = {"dateTime": args["start"]}
        if args.get("end"): ev["end"] = {"dateTime": args["end"]}
        if args.get("attendees"):
            ev["attendees"] = [{"email": a} for a in args["attendees"] if "@" in (a or "")]
        up = svc.events().update(calendarId=cid, eventId=args["eventId"], body=ev,
                                 sendUpdates="all").execute()
        return {"eventId": up.get("id"), "updated": True, "status": up.get("status")}

    def op_calendar_cancel(self, args, account):
        self._require_live()
        svc = self._svc("calendar", "v3")
        cid = args.get("calendarId", "primary")
        ev = svc.events().get(calendarId=cid, eventId=args["eventId"]).execute()
        if ev.get("recurringEventId"):
            svc.events().update(calendarId=cid, eventId=args["eventId"],
                                body={**ev, "status": "cancelled"}).execute()
        else:
            svc.events().delete(calendarId=cid, eventId=args["eventId"]).execute()
        return {"cancelled": True, "eventId": args["eventId"]}

    def op_calendar_availability(self, args, account):
        self._require_live()
        import datetime
        from datetime import timezone as _tz
        t0 = datetime.datetime.fromisoformat(args["timeMin"].replace("Z", "+00:00"))
        t1 = datetime.datetime.fromisoformat(args["timeMax"].replace("Z", "+00:00"))
        if t0.tzinfo is None:
            t0 = t0.astimezone()
        if t1.tzinfo is None:
            t1 = t1.astimezone()
        svc = self._svc("calendar", "v3")
        body = {"timeMin": t0.astimezone().isoformat(),
                "timeMax": t1.astimezone().isoformat(),
                "timeZone": self.settings.timezone,
                "items": [{"id": args.get("calendarId", "primary")}]}
        free = svc.freebusy().query(body=body).execute()
        busy = []
        for c, ranges in free.get("calendars", {}).items():
            busy += ranges.get("busy", [])
        slots = []
        cur = t0
        dur = datetime.timedelta(minutes=args.get("durationMin", 30))
        while cur + dur <= t1:
            ok = True
            for b in busy:
                bs = datetime.datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
                be = datetime.datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
                if not (cur + dur <= bs or cur >= be):
                    ok = False; break
            if ok:
                slots.append({"start": cur.isoformat(), "end": (cur + dur).isoformat()})
            cur += dur
        return {"busy": busy, "free_slots": slots[:20]}

    # ---- Drive -------------------------------------------------------- #
    def op_drive_search(self, args, account):
        self._require_live()
        svc = self._svc("drive", "v3")
        qparts = []
        if args.get("query"): qparts.append(f"({args['query']})")
        if args.get("name"): qparts.append(f"name contains '{args['name'].replace(chr(39), '')}'")
        if args.get("mimeType"): qparts.append(f"mimeType='{args['mimeType']}'")
        q = " and ".join(qparts) if qparts else None
        res = svc.files().list(q=q, pageSize=args.get("maxResults", 50),
                               fields="files(id,name,mimeType,modifiedTime,size,"
                                      "webViewLink)").execute()
        return {"files": res.get("files", [])}

    def op_drive_read(self, args, account):
        self._require_live()
        svc = self._svc("drive", "v3")
        f = svc.files().get(fileId=args["fileId"], fields="id,name,mimeType,webViewLink").execute()
        mime = f.get("mimeType", "")
        content = None
        if mime == "application/vnd.google-apps.document":
            r = svc.files().export(fileId=args["fileId"], mimeType="text/plain").execute()
            content = r.decode("utf-8", "replace") if isinstance(r, bytes) else r
        elif mime == "application/vnd.google-apps.spreadsheet":
            content = "spreadsheet - read ranges via google.sheets.read"
        else:
            try:
                r = svc.files().get_media(fileId=args["fileId"]).execute()
                content = base64.b64encode(r).decode() if isinstance(r, bytes) else str(r)
            except Exception:
                content = None
        return {"file": f, "content": content}

    def op_drive_download(self, args, account):
        self._require_live()
        svc = self._svc("drive", "v3")
        r = svc.files().get_media(fileId=args["fileId"]).execute()
        return {"fileId": args["fileId"], "content_base64": base64.b64encode(r).decode()}

    def _docs_create(self, title, content, folder_id):
        drive = self._svc("drive", "v3")
        meta = {"name": title, "mimeType": "application/vnd.google-apps.document"}
        if folder_id: meta["parents"] = [folder_id]
        f = drive.files().create(body=meta).execute()
        if content:
            docs = self._svc("docs", "v1")
            docs.documents().batchUpdate(documentId=f["id"], body={
                "requests": [{"insertText": {"location": {"index": 1},
                                             "text": content}}]}).execute()
        return f

    def op_docs_create(self, args, account):
        self._require_live()
        f = self._docs_create(args["title"], args.get("content", ""), args.get("folderId"))
        return {"fileId": f["id"], "url": f"https://docs.google.com/document/d/{f['id']}/edit"}

    def op_docs_read(self, args, account):
        self._require_live()
        docs = self._svc("docs", "v1")
        d = docs.documents().get(documentId=args["fileId"]).execute()
        text = "".join(e.get("textRun", {}).get("content", "")
                       for e in d.get("body", {}).get("content", [])
                       if "textRun" in e)
        return {"documentId": args["fileId"], "title": d.get("title"), "text": text}

    # ---- Sheets ------------------------------------------------------- #
    def op_sheets_read(self, args, account):
        self._require_live()
        sh = self._svc("sheets", "v4")
        r = sh.spreadsheets().values().get(spreadsheetId=args["spreadsheetId"],
                                           range=args["range"]).execute()
        return {"values": r.get("values", [])}

    def op_sheets_search(self, args, account):
        self._require_live()
        sh = self._svc("sheets", "v4")
        r = sh.spreadsheets().values().get(spreadsheetId=args["spreadsheetId"],
                                           range=args["range"]).execute()
        rows = r.get("values", []); term = args["term"].lower()
        hits = [{"row": i + 1, "values": row} for i, row in enumerate(rows)
                if any(term in str(c).lower() for c in row)]
        return {"matches": hits}

    def op_sheets_write(self, args, account):
        self._require_live()
        sh = self._svc("sheets", "v4")
        body = {"range": args["range"], "values": args["values"]}
        sh.spreadsheets().values().update(spreadsheetId=args["spreadsheetId"],
                                          range=args["range"], body=body,
                                          valueInputOption="RAW").execute()
        return {"updated": True, "range": args["range"]}

    def op_sheets_append(self, args, account):
        self._require_live()
        sh = self._svc("sheets", "v4")
        sh.spreadsheets().values().append(spreadsheetId=args["spreadsheetId"],
                                          range=args["range"], body={"values": [args["values"]]},
                                          valueInputOption="RAW").execute()
        return {"appended": True, "range": args["range"]}

    # ---- Contacts ----------------------------------------------------- #
    def op_contacts_search(self, args, account):
        self._require_live()
        p = self._svc("people", "v1")
        res = p.people().searchContacts(query=args["query"], pageSize=args.get("pageSize", 20),
                                        readMask="names,emailAddresses,phoneNumbers,metadata").execute()
        return {"results": res.get("results", [])}

    def op_contacts_resolve(self, args, account):
        self._require_live()
        res = self.op_contacts_search({"query": args["name"], "pageSize": 10}, account)
        people = []
        for r in res["results"]:
            p = r["person"]
            people.append({
                "name": (p.get("names") or [{}])[0].get("displayName"),
                "emails": [e.get("value") for e in p.get("emailAddresses", [])],
                "phones": [ph.get("value") for ph in p.get("phoneNumbers", [])],
                "resource": p.get("resourceName"),
            })
        if len(people) == 1:
            return {"resolved": people[0], "ambiguous": False}
        return {"resolved": None, "ambiguous": True, "candidates": people,
                "note": "Confirm which contact before using phone/email."}

    # ---- Tasks -------------------------------------------------------- #
    def _tasklist(self):
        tk = self._svc("tasks", "v1")
        lists = tk.tasklists().list().execute()
        tl = (lists.get("items") or [{}])[0].get("id")
        return tk, tl

    def op_tasks_create(self, args, account):
        self._require_live()
        tk, tl = self._tasklist()
        body = {"title": args["title"]}
        if args.get("due"):
            body["due"] = (args["due"] if "T" in args["due"]
                           else args["due"] + "T00:00:00.000Z")
        if args.get("notes"): body["notes"] = args["notes"]
        t = tk.tasks().insert(tasklist=tl, body=body).execute()
        return {"taskId": t.get("id"), "title": t.get("title"), "due": t.get("due")}

    def op_tasks_list(self, args, account):
        self._require_live()
        tk, tl = self._tasklist()
        res = tk.tasks().list(tasklist=tl, maxResults=args.get("maxResults", 100)).execute()
        return {"tasks": res.get("items", [])}

    def _task_id(self, tk, tl, tid):
        t = tk.tasks().get(tasklist=tl, task=tid).execute()
        return t

    def op_tasks_complete(self, args, account):
        self._require_live()
        tk, tl = self._tasklist()
        t = tk.tasks().get(tasklist=tl, task=args["taskId"]).execute()
        t["status"] = "completed"
        tk.tasks().update(tasklist=tl, task=args["taskId"], body=t).execute()
        return {"completed": True, "taskId": args["taskId"]}

    def op_tasks_delete(self, args, account):
        self._require_live()
        tk, tl = self._tasklist()
        tk.tasks().delete(tasklist=tl, task=args["taskId"]).execute()
        return {"deleted": True, "taskId": args["taskId"]}

    # ---- Google Chat ------------------------------------------------ #
    def op_chat_send(self, args, account):
        self._require_live()
        chat = self._svc("chat", "v1")
        res = chat.spaces().messages().create(parent=args["space"],
                                              body={"text": args["text"]}).execute()
        return {"messageId": res.get("name"), "sent": True}
