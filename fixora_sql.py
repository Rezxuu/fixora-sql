#!/usr/bin/env python3
"""
Fixora - SQL port: login + role homepages (User / Mechanic / Admin).
Mirrors the real Firebase app's auth and the three role landing screens,
on SQLite with hashed passwords + parameterized queries. DB file: fixora.db
Run:  python3 fixora_sql.py  ->  http://localhost:5000
"""
import http.server, socketserver, sqlite3, urllib.parse, html, hashlib, secrets, datetime

import os
PORT=int(os.environ.get("PORT","5000")); DBFILE="fixora.db"
def hash_pw(password, salt=None):
    salt = salt or secrets.token_hex(16)
    return hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),200_000).hex(), salt

conn=sqlite3.connect(DBFILE, check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT, displayName TEXT, firstName TEXT, lastName TEXT, birthday TEXT,
 phone TEXT, email TEXT UNIQUE, password_hash TEXT, salt TEXT, role TEXT DEFAULT 'user',
 photoURL TEXT DEFAULT '', emailVerified INTEGER DEFAULT 0, suspended INTEGER DEFAULT 0, createdAt TEXT)""")
conn.commit()
def seed(email,pw,first,last,role,verified=1):
    if conn.execute("SELECT 1 FROM users WHERE email=?",(email,)).fetchone(): return
    h,s=hash_pw(pw)
    conn.execute("""INSERT INTO users(displayName,firstName,lastName,birthday,phone,email,password_hash,salt,role,emailVerified,createdAt)
      VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(f"{first} {last}",first,last,"01/01/2000","",email,h,s,role,verified,
      datetime.datetime.utcnow().isoformat()))
    conn.commit()
seed("admin@fixora.com","Admin12345","Charles","Lorenz","admin")
seed("mechanic@fixora.com","Mechanic123","Juan","Dela Cruz","mechanic")
seed("user@fixora.com","User12345","Maria","Santos","user")
seed("pedro@fixora.com","Pedro12345","Pedro","Reyes","user")
seed("ramon@fixora.com","Ramon12345","Ramon","Cruz","mechanic",0)

LOGO="data:image/png;base64,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"

CSS="""<style>
 *{box-sizing:border-box} body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:#f2f2f2;display:flex;justify-content:center}
 .phone{width:100%;max-width:440px;min-height:100vh;background:#f2f2f2;padding-bottom:30px}
 .header{background:#E3000F;text-align:center;padding:26px 20px 70px}.header img{width:150px;display:block;margin:0 auto}
 .header h2{color:#fff;font-size:1.7rem;margin:.2rem 0 .3rem;font-weight:800}.header p{color:#ffd9dc;margin:0;font-size:.9rem}
 .card{background:#f2f2f2;border-radius:26px 26px 0 0;margin-top:-46px;padding:24px 20px 20px}
 label{display:block;font-weight:700;font-size:.9rem;color:#222;margin:.8rem 0 .35rem}
 input,select{width:100%;padding:13px;border:0;border-radius:12px;background:#fff;font-size:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 .btn{width:100%;margin-top:18px;padding:14px;border:0;border-radius:12px;background:#E3000F;color:#fff;font-size:1.05rem;font-weight:800;cursor:pointer}
 .foot{text-align:center;margin-top:16px;font-size:.9rem;color:#333}.foot a{color:#E3000F;font-weight:800;text-decoration:none}
 .err{background:#fde7ea;color:#c20017;padding:11px 13px;border-radius:10px;font-size:.88rem;margin-bottom:6px;font-weight:600}
 .ok{background:#e7f9ee;color:#0a7a3a;padding:11px 13px;border-radius:10px;font-size:.88rem;margin-bottom:6px;font-weight:600}
 /* app bar */
 .bar{background:#E3000F;color:#fff;padding:16px 18px;display:flex;align-items:center;justify-content:space-between}
 .bar .t{font-weight:800;font-size:1.15rem}.bar .s{font-size:.8rem;color:#ffd9dc}
 .bar a{color:#fff;font-size:.8rem;text-decoration:none;border:1px solid #ffffff66;padding:5px 10px;border-radius:8px}
 .wrap{padding:16px}
 .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
 .stat{background:#fff;border-radius:14px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 .stat .n{font-size:1.6rem;font-weight:800;color:#E3000F}.stat .l{font-size:.78rem;color:#666;margin-top:2px}
 .sec{font-weight:800;color:#1a1a1a;margin:18px 2px 8px;font-size:1rem}
 .row{background:#fff;border-radius:12px;padding:12px 14px;margin-bottom:8px;box-shadow:0 1px 2px rgba(0,0,0,.06);display:flex;justify-content:space-between;align-items:center}
 .row small{color:#777}
 .pill{font-size:.7rem;font-weight:700;padding:3px 9px;border-radius:999px}
 .pg{background:#e7f9ee;color:#0a7a3a}.pr{background:#fde7ea;color:#c20017}.py{background:#fff4d6;color:#9a6b00}
 .tile{background:#fff;border-radius:16px;padding:18px 14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08);font-weight:700;color:#1a1a1a}
 .tile .i{font-size:1.7rem}.srch{width:100%;padding:13px 14px;border:0;border-radius:12px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08);margin:6px 0 14px}
 .big{background:#E3000F;color:#fff;border-radius:14px;padding:16px;text-align:center;font-weight:800;margin-top:8px} .motto{background:#E3000F;color:#fff;border-radius:16px;padding:16px 18px;margin:0 0 4px} .motto .m{font-weight:800;font-size:1.05rem}.motto .s{font-size:.82rem;color:#ffe0e0;margin-top:3px} .fab{position:fixed;right:calc(50% - 210px);bottom:22px;width:56px;height:56px;border-radius:50%;background:#E3000F;color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 4px 14px rgba(0,0,0,.3);text-decoration:none} @media(max-width:460px){.fab{right:18px}} .twobtn{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px} .bo{background:#fff;color:#E3000F;border:2px solid #E3000F;border-radius:14px;padding:14px;text-align:center;font-weight:800} .nav{display:flex;justify-content:space-around;background:#fff;border-radius:14px;margin-top:16px;padding:12px 0;box-shadow:0 1px 3px rgba(0,0,0,.08)} .nav a{color:#555;text-decoration:none;font-size:.82rem;font-weight:700;text-align:center}.nav .ic{font-size:1.2rem;display:block} .ubar{background:#E3000F;padding:18px 18px 16px;display:flex;align-items:center;justify-content:space-between} .ubar .brand{color:#F2B705;font-weight:900;font-size:1.3rem;letter-spacing:1px;line-height:1} .ubar .brand small{display:block;color:#fff;font-weight:600;font-size:.62rem;letter-spacing:1px;margin-top:2px} .ubar .hi{color:#fff;font-weight:700;font-size:.95rem;margin-right:10px} .ubar .av{width:40px;height:40px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-size:1.2rem} .ucard{background:#fff;border-radius:16px;padding:16px 18px;margin:0 16px 12px;box-shadow:0 1px 3px rgba(0,0,0,.08)} .uwrap{padding:14px 0 90px} .loc{display:flex;flex-direction:column} .loc .lab{color:#E3000F;font-size:.8rem;font-weight:700}.loc .val{font-weight:800;margin-top:3px} .usec{font-weight:800;font-size:1.15rem;margin:6px 16px 10px} .ugrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:0 16px} .utile{background:#fff;border-radius:16px;padding:22px 14px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.08)} .utile .ic{width:54px;height:54px;border-radius:50%;background:#FFE0E0;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin:0 auto 10px} .utile .nm{font-weight:800;color:#1a1a1a} .emstate{text-align:center;padding:60px 30px;color:#555}.emstate .bx{width:66px;height:66px;border:2px solid #d8d8d8;border-radius:10px;margin:0 auto 18px} .emstate h3{color:#1a1a1a;font-size:1.3rem;margin:0 0 8px}.emstate p{color:#888;font-size:.95rem;margin:0} .bookbtn{display:inline-block;margin-top:18px;background:#E3000F;color:#fff;font-weight:800;padding:13px 26px;border-radius:999px;text-decoration:none} .ufab{position:fixed;right:calc(50% - 205px);bottom:86px;width:58px;height:58px;border-radius:50%;background:#1a2230;color:#9fb4ff;display:flex;align-items:center;justify-content:center;font-size:1.4rem;box-shadow:0 4px 14px rgba(0,0,0,.35);text-decoration:none} @media(max-width:460px){.ufab{right:20px}} .tabs{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:440px;background:#fff;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #eee} .tabs a{color:#9a9a9a;text-decoration:none;font-size:.72rem;font-weight:700;text-align:center}.tabs a .ic{display:block;font-size:1.15rem;margin-bottom:2px} .tabs a.on{color:#E3000F} .utile{cursor:pointer;transition:.12s} .utile.on{border:2px solid #E3000F;background:#fff5f5} .utile.on .ic{background:#E3000F;color:#fff}.utile.on .nm{color:#E3000F} .reqbtn{display:block;margin:18px 16px 0;background:#E3000F;color:#fff;border-radius:14px;padding:16px;text-align:center;font-weight:800;text-decoration:none} .chip2{display:inline-flex;align-items:center;gap:6px;background:#ffffff33;color:#fff;font-weight:700;font-size:.8rem;padding:5px 12px;border-radius:999px;margin-top:8px} .spin{width:46px;height:46px;border:4px solid #f0c9cd;border-top-color:#E3000F;border-radius:50%;margin:0 auto;animation:sp 1s linear infinite}@keyframes sp{to{transform:rotate(360deg)}} .sheet{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:440px;background:#fff;border-radius:22px 22px 0 0;padding:20px 18px 26px;box-shadow:0 -4px 20px rgba(0,0,0,.12)} .feat{display:flex;justify-content:space-around;margin:14px 0;text-align:center}.feat .fi{font-size:1.15rem}.feat .ft{font-size:.72rem;color:#666;margin-top:3px} .findbtn{display:block;width:100%;border:0;border-radius:14px;padding:15px;font-weight:800;font-size:1rem;color:#fff;cursor:pointer}
</style>"""
def page(b): return "<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'><title>Fixora</title>"+CSS+"</head><body><div class=phone>"+b+"</div></body></html>"
def head(sub): return f'<div class="header"><img src="{LOGO}"><h2>Welcome!</h2><p>{sub}</p></div>'
def bar(title,sub): return f'<div class="bar"><div><div class="t">{title}</div><div class="s">{sub}</div></div><a href="/">Log out</a></div>'

def login_body(err="",ok="",email=""):
    m=(f'<div class="err">{html.escape(err)}</div>' if err else '')+(f'<div class="ok">{html.escape(ok)}</div>' if ok else '')
    return head("Log in to your account")+'<div class="card">'+m+('<form method=POST action=/login>'
      f'<label>Email</label><input name=email value="{html.escape(email)}" autocomplete=off>'
      '<label>Password</label><input name=password type=password autocomplete=off>'
      '<button class=btn>Log In</button></form>'
      '<div class=foot>Don\'t have an account? <a href="/register">Sign up</a></div></div>')
def register_body(err="",f=None):
    f=f or {}; g=lambda k: html.escape(f.get(k,[""])[0])
    m=f'<div class="err">{html.escape(err)}</div>' if err else ''
    return head("Create your account")+'<div class="card">'+m+('<form method=POST action=/register>'
      f'<label>First name</label><input name=firstName value="{g("firstName")}">'
      f'<label>Last name</label><input name=lastName value="{g("lastName")}">'
      f'<label>Email</label><input name=email value="{g("email")}">'
      '<label>Password</label><input name=password type=password>'
      '<label>Role</label><select name=role><option value=user>User</option><option value=mechanic>Mechanic</option></select>'
      '<button class=btn>Sign Up</button></form>'
      '<div class=foot>Already have an account? <a href="/">Log in</a></div></div>')


def ubar(name):
    return (f'<div class="ubar"><div class="brand">FIX&#9733;RA<small>ROADSIDE ASSISTANCE</small></div>'
            f'<div style="display:flex;align-items:center"><span class="hi">Hi, {html.escape(name)}</span>'
            f'<span class="av">&#128100;</span></div></div>')
def utabs(active):
    items=[("home","Home","&#127968;"),("service","Service","&#128295;"),("recent","Recent","&#128197;"),("messages","Messages","&#128172;")]
    a="".join(f'<a href="/{k}" class="{ "on" if k==active else "" }"><span class="ic">{i}</span>{lbl}</a>' for k,lbl,i in items)
    return f'<div class="tabs">{a}</div>'
def ufab():
    return '<a class="ufab" href="/service" title="Chat / Request">&#128172;</a>'

PICK = '<script>function pick(el){document.querySelectorAll(".utile").forEach(t=>t.classList.remove("on"));el.classList.add("on");var s=el.dataset.s;var b=document.getElementById("reqbtn");b.style.display="block";b.style.background="#E3000F";b.style.color="#fff";b.innerHTML="Request "+s;b.href="/request?service="+encodeURIComponent(s);}</script>'

def _tiles():
    cats=[("&#128295;","Mechanic"),("&#9981;","Fuel Delivery"),("&#128267;","Battery Jumpstart"),("&#128668;","Towing")]
    return "".join(f'<div class="utile" data-s="{n}" onclick="pick(this)"><div class="ic">{i}</div><div class="nm">{n}</div></div>' for i,n in cats)

def home_user(u):
    return ubar(u['firstName'])+('<div class="uwrap">'
      '<div class="ucard" style="text-align:center"><div style="color:#E3000F;font-weight:900;font-size:1.15rem">Emergency? We\'ve got you.</div>'
      '<div style="color:#555;font-size:.9rem;margin-top:4px">Select a service and help will be on the way instantly.</div></div>'
      '<div class="ucard"><div class="loc"><span class="lab">&#128205; Your Location</span><span class="val">Marikina City, NCR</span></div></div>'
      '<div class="usec">What do you need?</div>'
      f'<div class="ugrid">{_tiles()}</div>'
      '<a id="reqbtn" class="reqbtn" style="display:none" href="#">Request</a>'
      '</div>'+PICK)+ufab()+utabs("home")

def u_service(u):
    return ('<div class="ubar" style="justify-content:center"><div style="color:#fff;font-weight:800;font-size:1.25rem">Request a Service</div></div>'
      '<div class="uwrap">'
      '<div class="ucard"><div class="loc"><span class="lab">&#128205; Your Location</span><span class="val">Marikina City, NCR</span></div></div>'
      '<div class="usec">Select a Service</div>'
      f'<div class="ugrid">{_tiles()}</div>'
      '<div class="usec" style="margin-top:18px">Additional Notes</div>'
      '<div style="padding:0 16px"><textarea placeholder="Describe your issue (optional)..." style="width:100%;min-height:90px;border:0;border-radius:12px;padding:14px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08);font-family:inherit"></textarea>'
      '<div style="background:#eef3ff;color:#3355aa;padding:11px 13px;border-radius:10px;font-size:.82rem;margin-top:10px">&#9432; The more details you provide, the faster the mechanic can help.</div></div>'
      '<a id="reqbtn" class="reqbtn" style="background:#cfcfcf;color:#fff" href="#">Select a Service First</a>'
      '</div>'+PICK)+ufab()+utabs("service")

def u_request(service):
    s=html.escape(service or "Mechanic"); sq=urllib.parse.quote(s)
    return ('<div class="ubar" style="flex-direction:column;align-items:flex-start;gap:4px">'
      '<div style="display:flex;align-items:center;gap:10px"><a href="/home" style="color:#fff;text-decoration:none;font-size:1.3rem">&#8592;</a>'
      '<span style="color:#fff;font-weight:800;font-size:1.25rem">Request Service</span></div>'
      f'<span class="chip2">&#128295; {s}</span></div>'
      '<div style="padding:80px 20px 150px;text-align:center" id="locbox">'
      '<div class="spin"></div><div style="color:#777;margin-top:14px">Getting your location...</div></div>'
      '<div class="sheet"><div style="display:flex;align-items:center;gap:12px">'
      '<div style="width:48px;height:48px;border-radius:50%;background:#FFE0E0;display:flex;align-items:center;justify-content:center;font-size:1.3rem">&#128295;</div>'
      f'<div><div style="font-weight:800;font-size:1.15rem">{s}</div>'
      '<div style="color:#777;font-size:.85rem">Verified mechanics nearby will receive your request</div></div></div>'
      '<div style="border-top:1px solid #eee;margin:14px 0"></div>'
      '<div class="feat"><div><div class="fi">&#128205;</div><div class="ft">Your location</div></div>'
      '<div><div class="fi" style="color:#22C55E">&#10003;</div><div class="ft">Verified mechanics</div></div>'
      '<div><div class="fi" style="color:#F59E0B">&#9889;</div><div class="ft">Fast response</div></div></div>'
      f'<button class="findbtn" id="findbtn" disabled style="background:#cfcfcf" onclick="location.href=\'/sent?service={sq}\'">&#128269; Locating...</button></div>'
      '<script>setTimeout(function(){var b=document.getElementById("findbtn");b.disabled=false;b.style.background="#E3000F";b.innerHTML="&#128269; Find Mechanics Near Me";document.getElementById("locbox").innerHTML="<div style=\'font-size:2.2rem;color:#22C55E\'>&#128205;</div><div style=\'color:#444;margin-top:8px;font-weight:700\'>Marikina City, NCR</div>";},1800);</script>')

def u_sent(service):
    s=html.escape(service or "Mechanic")
    return ('<div class="ubar" style="justify-content:center"><div style="color:#fff;font-weight:800;font-size:1.25rem">Request Sent</div></div>'
      '<div class="uwrap"><div class="emstate"><div style="font-size:3rem;color:#22C55E">&#10003;</div>'
      f'<h3 style="margin-top:10px">Request sent!</h3><p>Your {s.lower()} request has been sent to verified mechanics nearby. You\'ll be notified when one accepts.</p>'
      '<a class="bookbtn" href="/home">Back to Home</a></div></div>')+utabs("recent")

def u_recent(u):
    return ('<div class="ubar" style="justify-content:center"><div style="color:#fff;font-weight:800;font-size:1.25rem">My Bookings</div></div>'
      '<div class="uwrap"><div class="emstate"><div class="bx"></div>'
      '<h3>No bookings yet</h3><p>Your service history will appear here once you book a mechanic.</p></div></div>')+ufab()+utabs("recent")

def u_messages(u):
    return ('<div class="ubar" style="justify-content:center"><div style="color:#fff;font-weight:800;font-size:1.25rem">Messages</div></div>'
      '<div class="uwrap"><div class="emstate"><div class="bx"></div>'
      '<h3>No messages yet</h3><p>Your conversations with mechanics will appear here.</p>'
      '<a class="bookbtn" href="/service">Book a Service</a></div></div>')+ufab()+utabs("messages")

def home_mechanic(u):
    return bar("Mechanic Dashboard",f"Hi, {html.escape(u['firstName'])}")+('<div class="wrap">'
      '<div class="grid3">'
      '<div class="stat"><div class="n">12</div><div class="l">Jobs Done</div></div>'
      '<div class="stat"><div class="n">&#8369;8.4k</div><div class="l">Earnings</div></div>'
      '<div class="stat"><div class="n">4.8</div><div class="l">Rating</div></div></div>'
      '<div class="sec">Active Job</div>'
      '<div class="row"><div>Battery Jumpstart<br><small>Antipolo St., Marikina</small></div><span class="pill py">In progress</span></div>'
      '<div class="twobtn"><div class="big" style="margin-top:0">Start Service</div><div class="bo">Mark Complete</div></div>'
      '<div class="sec">Incoming Requests</div>'
      '<div class="row"><div>Towing <span class="pill pr">NEW</span><br><small>2.1 km away</small></div>'
      '<div><a href="#" style="color:#888;text-decoration:none;margin-right:10px">Ignore</a><a href="#" style="color:#E3000F;font-weight:800;text-decoration:none">Accept</a></div></div>'
      '<div class="row"><div>Fuel Delivery <span class="pill pr">NEW</span><br><small>3.4 km away</small></div>'
      '<div><a href="#" style="color:#888;text-decoration:none;margin-right:10px">Ignore</a><a href="#" style="color:#E3000F;font-weight:800;text-decoration:none">Accept</a></div></div>'
      '<div class="sec">Job History</div>'
      '<div class="row"><div>Towing &mdash; EDSA<br><small>Yesterday</small></div><span class="pill pg">Completed</span></div>'
      '<div class="row"><div>Battery &mdash; Cubao<br><small>2 days ago</small></div><span class="pill pg">Completed</span></div>'
      '<div class="nav"><a href="#"><span class="ic">&#128100;</span>My Profile</a>'
      '<a href="#"><span class="ic">&#128172;</span>Messages</a>'
      '<a href="#"><span class="ic">&#10067;</span>Help</a></div></div>')

def home_admin(u):
    total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    mechs=conn.execute("SELECT COUNT(*) FROM users WHERE role='mechanic'").fetchone()[0]
    verified=conn.execute("SELECT COUNT(*) FROM users WHERE emailVerified=1").fetchone()[0]
    suspended=conn.execute("SELECT COUNT(*) FROM users WHERE suspended=1").fetchone()[0]
    rows=conn.execute("SELECT displayName,email,role FROM users ORDER BY id DESC LIMIT 6").fetchall()
    ulist="".join(f'<div class="row"><div>{html.escape(d or "")}<br><small>{html.escape(e)}</small></div><span class="pill {"pr" if r=="admin" else "pg" if r=="mechanic" else "py"}">{r}</span></div>' for d,e,r in rows)
    return bar("Fixora Dashboard","Admin Panel")+('<div class="wrap">'
      '<div class="grid">'
      f'<div class="stat"><div class="n">{total}</div><div class="l">Total Users</div></div>'
      f'<div class="stat"><div class="n">{mechs}</div><div class="l">Mechanics</div></div>'
      f'<div class="stat"><div class="n">{verified}</div><div class="l">Verified</div></div>'
      f'<div class="stat"><div class="n">{suspended}</div><div class="l">Suspended</div></div></div>'
      '<div class="grid3" style="margin-top:12px">'
      '<div class="stat"><div class="n">3</div><div class="l">Online Now</div></div>'
      '<div class="stat"><div class="n">5</div><div class="l">Active Jobs</div></div>'
      '<div class="stat"><div class="n">&#8369;42k</div><div class="l">Revenue</div></div></div>'
      '<div class="sec">Users</div>'+ulist+
      '<div class="sec">Recent Bookings</div>'
      '<div class="row"><div>Towing — Pedro R.<br><small>Today 2:14 PM</small></div><span class="pill pg">Completed</span></div>'
      '<div class="row"><div>Battery — Maria S.<br><small>Today 11:02 AM</small></div><span class="pill py">Ongoing</span></div></div>')

HOME={"user":home_user,"mechanic":home_mechanic,"admin":home_admin}

class H(http.server.BaseHTTPRequestHandler):
    def _h(self,code,body):
        out=page(body).encode(); self.send_response(code)
        self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(out)))
        self.end_headers(); self.wfile.write(out)
    def _form(self):
        n=int(self.headers.get("Content-Length",0)); return urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8","replace"))
    def do_GET(self):
        parsed=urllib.parse.urlparse(self.path); path=parsed.path; q=urllib.parse.parse_qs(parsed.query)
        if path in ("/","/login"): return self._h(200,login_body())
        if path=="/register": return self._h(200,register_body())
        if path in ("/home","/service","/recent","/messages"):
            u={"firstName":"Test User","email":"user@fixora.com","role":"user"}
            return self._h(200,{"/home":home_user,"/service":u_service,"/recent":u_recent,"/messages":u_messages}[path](u))
        if path=="/request": return self._h(200,u_request(q.get("service",["Mechanic"])[0]))
        if path=="/sent": return self._h(200,u_sent(q.get("service",["Mechanic"])[0]))
        return self._h(404,'<div class="uwrap"><div class="emstate"><h3>404</h3></div></div>')

    def do_POST(self):
        if self.path=="/login":
            f=self._form(); email=f.get("email",[""])[0].strip(); pw=f.get("password",[""])[0]
            row=conn.execute("SELECT firstName,email,role,password_hash,salt FROM users WHERE email=?",(email,)).fetchone()
            if row:
                calc,_=hash_pw(pw,row[4])
                if secrets.compare_digest(calc,row[3]):
                    u={"firstName":row[0],"email":row[1],"role":row[2]}
                    return self._h(200, HOME.get(row[2],home_user)(u))
            return self._h(200, login_body(err="Invalid email or password.",email=email))
        if self.path=="/register":
            f=self._form(); first=f.get("firstName",[""])[0].strip(); last=f.get("lastName",[""])[0].strip()
            email=f.get("email",[""])[0].strip(); pw=f.get("password",[""])[0]; role=f.get("role",["user"])[0]
            if not(first and last and email and pw): return self._h(200,register_body("Please fill in all fields.",f))
            if role not in("user","mechanic"): role="user"
            if conn.execute("SELECT 1 FROM users WHERE email=?",(email,)).fetchone():
                return self._h(200,register_body("Email already registered.",f))
            h,s=hash_pw(pw)
            conn.execute("""INSERT INTO users(displayName,firstName,lastName,email,password_hash,salt,role,createdAt)
              VALUES(?,?,?,?,?,?,?,?)""",(f"{first} {last}",first,last,email,h,s,role,datetime.datetime.utcnow().isoformat()))
            conn.commit()
            return self._h(200, login_body(ok="Account created. Please log in.",email=email))
        return self._h(404,'<div class="wrap"><h2>404</h2></div>')
    def log_message(self,*a): return

socketserver.ThreadingTCPServer.allow_reuse_address=True
with socketserver.ThreadingTCPServer(("0.0.0.0",PORT),H) as httpd:
    print("Fixora SQL (login + 3 role homepages) on http://127.0.0.1:%d  [SQLite %s]"%(PORT,DBFILE))
    print("admin@fixora.com/Admin12345  mechanic@fixora.com/Mechanic123  user@fixora.com/User12345")
    try: httpd.serve_forever()
    except KeyboardInterrupt: print("\nStopped.")
