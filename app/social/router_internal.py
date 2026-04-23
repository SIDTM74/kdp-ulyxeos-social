import json
import traceback
from fastapi import APIRouter, HTTPException, Request
from app.config import INTERNAL_AUTPOST_SECRET
from app.db import get_db
from app.utils import now_iso, save_log
from app.social_generator import generate_social_post
from app.social_storage import get_active_media_for_platform, mark_media_used
from app.mailer import send_social_report_email
from app.social.publisher_facebook import FacebookPublisher
from app.social.publisher_instagram import InstagramPublisher
from app.social.publisher_tiktok import TikTokPublisher
from app.auth import is_admin_authenticated

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/autopost/run")
def run_autopost(request: Request):
    received_secret = request.headers.get("x-internal-secret", "").strip()
    expected_secret = (INTERNAL_AUTPOST_SECRET or "").strip()
    admin_ok = is_admin_authenticated(request)

    if not admin_ok and received_secret != expected_secret:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Forbidden",
                "received_present": bool(received_secret),
                "received_length": len(received_secret),
                "expected_present": bool(expected_secret),
                "expected_length": len(expected_secret),
            },
        )

    conn = None
    run_id = None

    try:
        conn = get_db()
        cur = conn.cursor()

        started_at = now_iso()
        cur.execute("""
            INSERT INTO social_runs (trigger_type, started_at, status, summary)
            VALUES (?, ?, ?, ?)
        """, ("cron", started_at, "running", ""))
        run_id = cur.lastrowid
        conn.commit()

        text = generate_social_post()

        cur.execute("SELECT * FROM social_settings WHERE id = 1")
        settings = cur.fetchone()

        media_instagram = get_active_media_for_platform("instagram", conn=conn)
        media_tiktok = get_active_media_for_platform("tiktok", conn=conn)
        media_facebook = get_active_media_for_platform("facebook", conn=conn)

        publishers = []

        if settings["facebook_enabled"]:
            publishers.append((FacebookPublisher(), media_facebook))
        if settings["instagram_enabled"]:
            publishers.append((InstagramPublisher(), media_instagram))
        if settings["tiktok_enabled"]:
            publishers.append((TikTokPublisher(), media_tiktok))

        chosen_media_id = None
        if media_instagram:
            chosen_media_id = media_instagram["id"]
        elif media_tiktok:
            chosen_media_id = media_tiktok["id"]
        elif media_facebook:
            chosen_media_id = media_facebook["id"]

        sentence_count = len([x for x in text.replace("?", ".").replace("!", ".").split(".") if x.strip()])

        cur.execute("""
            INSERT INTO social_posts (content_text, sentence_count, media_id, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (text, sentence_count, chosen_media_id, now_iso(), "drafted"))
        social_post_id = cur.lastrowid
        conn.commit()

        results = []

        for publisher, media in publishers:
            result = publisher.publish(text=text, media=media)
            results.append(result)

            cur.execute("""
                INSERT INTO social_post_targets (
                    social_post_id, platform, platform_post_id, status, response_json, sent_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                social_post_id,
                publisher.platform_name,
                result.get("platform_post_id"),
                result["status"],
                json.dumps(result["response"], ensure_ascii=False),
                now_iso()
            ))

            if media and result["status"] == "success":
                mark_media_used(media["id"], conn=conn)

        final_status = "success"
        if any(r["status"] == "failed" for r in results):
            final_status = "partial" if any(r["status"] == "success" for r in results) else "failed"

        cur.execute("""
            UPDATE social_posts SET status = ? WHERE id = ?
        """, ("sent" if final_status != "failed" else "failed", social_post_id))

        summary = {
            "run_id": run_id,
            "post_id": social_post_id,
            "text": text,
            "results": results,
        }

        cur.execute("""
            UPDATE social_runs
            SET finished_at = ?, status = ?, summary = ?
            WHERE id = ?
        """, (now_iso(), final_status, json.dumps(summary, ensure_ascii=False), run_id))

        conn.commit()

        save_log(f"run_{run_id}.json", summary)

        try:
            email_body = f"""Autopost terminé.

Texte envoyé :
{text}

Résultats :
{json.dumps(results, ensure_ascii=False, indent=2)}
"""
            send_social_report_email(
                subject=f"[KDP ULYXEOS] Autopost {final_status}",
                body=email_body
            )
        except Exception as mail_exc:
            print(f"Email error: {mail_exc}")

        return {
            "ok": True,
            "status": final_status,
            "text": text,
            "results": results
        }

    except Exception as exc:
        error_trace = traceback.format_exc()
        print(error_trace)

        if conn and run_id:
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE social_runs
                    SET finished_at = ?, status = ?, summary = ?
                    WHERE id = ?
                """, (
                    now_iso(),
                    "failed",
                    json.dumps({"error": str(exc), "traceback": error_trace}, ensure_ascii=False),
                    run_id
                ))
                conn.commit()
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "type": exc.__class__.__name__,
            },
        )

    finally:
        if conn:
            conn.close()
