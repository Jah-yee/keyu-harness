"""SIMULATED Feishu collaboration layer: groups, calendar with recurring meetings,
meeting links (reservation-with-renewal semantics), and join-by-link/calendar.

Basis for each behavior: env/FEISHU_CONJECTURE.md (A=reported, B=public capability, C=filler).
Fictional users only (intern-V / intern-C / researcher-L are role placeholders).
"""
from __future__ import annotations

from .events import EventBus


class FeishuSim:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.groups: dict[str, dict] = {}
        self.calendar: dict[str, list[dict]] = {}
        self.meetings: dict[str, dict] = {}
        self.messages: list[dict] = []
        self.attendance: list[dict] = []
        self._gid = 0
        self._link = 0

    # ---- groups (B: 飞书群基础能力; C: 成员/群名填充) ----
    def create_group(self, name: str, members: list[str]) -> str:
        self._gid += 1
        gid = f"oc_{self._gid:06d}"
        self.groups[gid] = {"name": name, "members": list(members)}
        self.bus.emit("feishu", "group_create", disclosure_id="D43", gid=gid, name=name, size=len(members))
        return gid

    def send_message(self, gid: str, sender: str, text: str, mentions: list[str] | None = None) -> dict:
        if sender not in self.groups[gid]["members"]:
            raise PermissionError(f"{sender} not in group {gid}")
        msg = {"gid": gid, "sender": sender, "text": text, "mentions": list(mentions or [])}
        self.messages.append(msg)
        self.bus.emit("feishu", "message", gid=gid, sender=sender, mentions=list(mentions or []))
        return msg

    # ---- calendar & meetings (B: 日历重复规则 + 预约续期; A: 固定链接+日历入口) ----
    def create_meeting(self, owner: str, title: str, *, recurring: bool = False,
                       occurrences: int = 1, link: str | None = None,
                       expiry_tick: int = 10_000) -> dict:
        """A calendar event with a video-meeting entry. Recurring events share one
        meeting link across occurrences (B: 日历重复规则). Links are reservation-style
        objects with a renewable expiry (B: VC 预约 API 的 30 天+续期语义, C: 时长填充)."""
        self._link += 1
        if link is None:
            link = f"https://vc.example-sim.internal/j/{self._link:09d}"
        self.meetings.setdefault(link, {"owner": owner, "title": title,
                                        "recurring": recurring, "expiry": expiry_tick,
                                        "renewals": 0, "participants_per_occurrence": []})
        events = []
        for occ in range(occurrences):
            ev = {"user": owner, "title": title, "occurrence": occ,
                  "meeting_link": link, "participants": [owner]}
            self.calendar.setdefault(owner, []).append(ev)
            events.append(ev)
        self.bus.emit("feishu", "calendar_event", disclosure_id="D36", owner=owner,
                      title=title, recurring=recurring, link=link, occurrences=occurrences)
        return {"link": link, "events": events}

    def invite(self, link: str, user: str, occurrence: int = 0) -> None:
        """被邀请者获得日历入口（A: 参会者的飞书日历含会议入口——LatePost 8-01 细节）。"""
        for ev in self.calendar.get(user, []):
            if ev["meeting_link"] == link and ev["occurrence"] == occurrence:
                ev["participants"].append(user)
                self.meetings[link]["participants_per_occurrence"].append((occurrence, user))
                return
        self.calendar.setdefault(user, []).append(
            {"user": user, "title": self.meetings[link]["title"], "occurrence": occurrence,
             "meeting_link": link, "participants": [user]})
        self.meetings[link]["participants_per_occurrence"].append((occurrence, user))

    def renew(self, link: str, extra_ticks: int = 10_000) -> None:
        self.meetings[link]["expiry"] += extra_ticks
        self.meetings[link]["renewals"] += 1

    def join_meeting(self, link: str, user: str, occurrence: int = 0) -> dict:
        """Join by link. Two access paths per the reported account: the link itself,
        and the calendar entry of any participant (A: LatePost). No org-wide ACL check
        beyond group/invite visibility is modelled — matching the reported lapse."""
        meeting = self.meetings.get(link)
        if meeting is None:
            raise KeyError(f"unknown meeting link {link}")
        via = "link"
        on_calendar = any(ev["meeting_link"] == link for ev in self.calendar.get(user, []))
        if on_calendar:
            via = "calendar"
        rec = self.bus.emit("feishu", "meeting_join", disclosure_id="D36", link=link,
                            user=user, occurrence=occurrence, via=via, expired=self.bus.now() > meeting["expiry"])
        self.attendance.append({"link": link, "user": user, "via": via, "ts": rec["ts"]})
        return rec
