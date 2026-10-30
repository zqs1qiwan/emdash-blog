#!/usr/bin/env python3
"""把 v4 配图换进已有文章：上传 → 按顺序替换 image block → 换封面 → 清理旧 media。

用法：python3 swap_figs_v4.py <slug> <fig1.webp,fig2.webp,...> <cover.webp>
"""
import json, os, subprocess, sys, hashlib, sqlite3
sys.path.insert(0, "/opt/data/blog-drafts")
from ulid_webp import ulid, webp_size

REPO = "/home/hermes/projects/laobaiblog"
DB = "laobaiblog-db"
BUCKET = "laobaiblog-media"
FIGDIR = "/opt/data/news/figures/v4/pub"
q = lambda s: "'" + str(s).replace("'", "''") + "'"

env = dict(os.environ)
for line in open("/opt/data/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

def d1(sql, json_out=True):
    cmd = ["npx", "wrangler", "d1", "execute", DB, "--remote", "--json", "--command", sql, "-y"]
    r = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True, timeout=180)
    if not json_out:
        return r.stdout
    s = r.stdout
    return json.loads(s[s.index("["):])[0]["results"]

def upload(path, alt, caption):
    w, h = webp_size(path)
    mid, vid = ulid(), ulid()
    key = f"{mid}.{vid}.webp"
    r = subprocess.run(["npx", "wrangler", "r2", "object", "put", f"{BUCKET}/{key}",
                        f"--file={path}", "--content-type=image/webp", "--remote"],
                       cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("UPLOAD FAIL", os.path.basename(path), r.stderr[-400:]); sys.exit(1)
    digest = "sha1:" + hashlib.sha1(open(path, "rb").read()).hexdigest()
    row = ("INSERT INTO media (id, filename, mime_type, size, width, height, alt, caption, storage_key, "
           "content_hash, created_at, author_id, status) VALUES "
           f"({q(mid)},{q(os.path.basename(path))},'image/webp',{os.path.getsize(path)},{w},{h},"
           f"{q(alt)},{q(caption)},{q(key)},{q(digest)},datetime('now'),NULL,'ready');")
    print(f"  up {os.path.basename(path):14s} {w}x{h} {os.path.getsize(path)}B")
    return {"id": mid, "key": key, "w": w, "h": h, "alt": alt, "caption": caption, "sql": row}

def main(slug, figs, cover, cover_alt, cover_cap):
    row = d1(f"SELECT id, content, featured_image FROM ec_posts WHERE slug = {q(slug)}")[0]
    pid, content, fi = row["id"], json.loads(row["content"]), row["featured_image"]
    old_ids = [b["asset"]["_ref"] for b in content if b["_type"] == "image"]
    old_cover = json.loads(fi)["id"] if fi else None
    print(f"post {pid}  旧图 {len(old_ids)} 张, 旧封面 {old_cover}")

    names = figs.split(",")
    assert len(names) == len(old_ids), f"图片数量不一致：配置 {len(names)} vs 正文 {len(old_ids)}"
    new = [upload(os.path.join(FIGDIR, n), "", "") for n in names]
    # 保留原 alt/caption
    for blk, m in zip([b for b in content if b["_type"] == "image"], new):
        m["alt"] = blk.get("alt", "")
        m["caption"] = blk.get("caption", "")

    cov = upload(os.path.join(FIGDIR, cover), cover_alt, cover_cap)

    blocks = [b for b in content if b["_type"] == "image"]
    for blk, m in zip(blocks, new):
        blk["asset"] = {"_type": "reference", "_ref": m["id"],
                        "url": f"/_emdash/api/media/file/{m['key']}", "provider": "local"}
        blk["width"], blk["height"] = m["w"], m["h"]

    featured = {"id": cov["id"], "provider": "local", "filename": cover, "mimeType": "image/webp",
                "width": cov["w"], "height": cov["h"], "alt": cover_alt,
                "meta": {"storageKey": cov["key"], "caption": cover_cap,
                         "blurhash": None, "dominantColor": None}}

    pt = json.dumps(content, ensure_ascii=False, separators=(",", ":"))
    sql = [m["sql"] for m in new] + [cov["sql"]]
    sql.append(f"UPDATE ec_posts SET content = {q(pt)}, featured_image = {q(json.dumps(featured, ensure_ascii=False))}, "
               f"updated_at = datetime('now') WHERE id = {q(pid)};")
    sqlfile = f"/opt/data/blog-drafts/swap-{slug}.sql"
    open(sqlfile, "w", encoding="utf-8").write("\n".join(sql) + "\n")

    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE ec_posts (id text primary key, content json, featured_image text, updated_at text)")
    db.execute("INSERT INTO ec_posts VALUES (?,?,?,?)", (pid, "[]", "{}", ""))
    db.executescript(sql[-1])
    back = json.loads(db.execute("SELECT content FROM ec_posts").fetchone()[0])
    print("roundtrip images:", sum(1 for b in back if b["_type"] == "image"),
          "| cover:", json.loads(db.execute("SELECT featured_image FROM ec_posts").fetchone()[0])["width"])

    print(subprocess.run(["bash", "-c", f"set -a; source /opt/data/.env; set +a; cd {REPO} && "
                          f"npx wrangler d1 execute {DB} --remote --file={sqlfile} -y"],
                         capture_output=True, text=True, timeout=300).stdout[-300:])

    json.dump({"post": pid, "slug": slug, "old_ids": old_ids + ([old_cover] if old_cover else []),
               "new_ids": [m["id"] for m in new] + [cov["id"]]},
              open(f"/opt/data/blog-drafts/swap-{slug}.json", "w"), indent=2)
    print("done", slug)

if __name__ == "__main__":
    slug = sys.argv[1]
    figs = sys.argv[2]
    cover = sys.argv[3]
    calt = sys.argv[4] if len(sys.argv) > 4 else ""
    ccap = sys.argv[5] if len(sys.argv) > 5 else ""
    main(slug, figs, cover, calt, ccap)
