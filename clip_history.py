"""
Clipboard History
===================
Sistem panosunu (clipboard) periyodik olarak izler ve her yeni kopyalanan
metni yerel bir SQLite veritabanında geçmiş olarak saklar. Daha sonra
geçmişi listeleyebilir, arayabilir ve istediğiniz bir girdiyi tekrar
panoya kopyalayabilirsiniz.

Kullanım:
    python clip_history.py watch                  # Arka planda izlemeye başla
    python clip_history.py list                    # Son 20 girdiyi göster
    python clip_history.py list --limit 50          # Son 50 girdiyi göster
    python clip_history.py search "fatura"          # Geçmişte ara
    python clip_history.py copy 5                   # 5 numaralı girdiyi panoya kopyala
    python clip_history.py clear                    # Tüm geçmişi temizle

Gereksinimler:
    pip install pyperclip
"""

import argparse
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import pyperclip

DB_PATH = Path.home() / ".clipboard_history.db"
POLL_INTERVAL = 1.0  # saniye
MAX_ENTRY_LENGTH = 10000  # Çok büyük içerikleri (örn. yanlışlıkla kopyalanan dosya) sınırla


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def watch():
    """Panoyu periyodik olarak kontrol eder, değişiklik olduğunda kaydeder."""
    conn = init_db()
    last_content = None

    print(f"Pano izleniyor... (veritabanı: {DB_PATH})")
    print("Durdurmak için Ctrl+C.\n")

    try:
        while True:
            try:
                current = pyperclip.paste()
            except Exception:
                current = None

            if current and current != last_content and current.strip():
                truncated = current[:MAX_ENTRY_LENGTH]
                conn.execute(
                    "INSERT INTO history (content, created_at) VALUES (?, ?)",
                    (truncated, datetime.now().isoformat()),
                )
                conn.commit()
                preview = truncated[:60].replace("\n", " ")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Kaydedildi: {preview}{'...' if len(truncated) > 60 else ''}")
                last_content = current

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nİzleme durduruldu.")
    finally:
        conn.close()


def list_entries(limit: int = 20):
    conn = init_db()
    rows = conn.execute(
        "SELECT id, content, created_at FROM history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()

    if not rows:
        print("Geçmişte henüz hiçbir kayıt yok. Önce 'watch' komutunu çalıştırın.")
        return

    for entry_id, content, created_at in rows:
        preview = content.replace("\n", " ⏎ ")[:80]
        timestamp = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
        print(f"[{entry_id:>4}] {timestamp}  {preview}{'...' if len(content) > 80 else ''}")


def search_entries(query: str):
    conn = init_db()
    rows = conn.execute(
        "SELECT id, content, created_at FROM history WHERE content LIKE ? ORDER BY id DESC",
        (f"%{query}%",),
    ).fetchall()
    conn.close()

    if not rows:
        print(f"'{query}' için sonuç bulunamadı.")
        return

    print(f"'{query}' için {len(rows)} sonuç bulundu:\n")
    for entry_id, content, created_at in rows:
        preview = content.replace("\n", " ⏎ ")[:80]
        timestamp = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
        print(f"[{entry_id:>4}] {timestamp}  {preview}{'...' if len(content) > 80 else ''}")


def copy_entry(entry_id: int):
    conn = init_db()
    row = conn.execute("SELECT content FROM history WHERE id = ?", (entry_id,)).fetchone()
    conn.close()

    if not row:
        print(f"ID {entry_id} bulunamadı.")
        return

    try:
        pyperclip.copy(row[0])
        print(f"Girdi #{entry_id} panoya kopyalandı.")
    except Exception as e:
        print(f"Panoya kopyalanamadı: {e}")


def show_entry(entry_id: int):
    conn = init_db()
    row = conn.execute("SELECT content, created_at FROM history WHERE id = ?", (entry_id,)).fetchone()
    conn.close()

    if not row:
        print(f"ID {entry_id} bulunamadı.")
        return

    content, created_at = row
    print(f"--- Girdi #{entry_id} ({created_at}) ---")
    print(content)


def clear_history():
    confirm = input("Tüm pano geçmişi silinecek. Onaylıyor musunuz? (evet/hayır): ")
    if confirm.lower() not in ("evet", "e", "yes", "y"):
        print("İptal edildi.")
        return

    conn = init_db()
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    print("Geçmiş temizlendi.")


def main():
    parser = argparse.ArgumentParser(description="Pano (clipboard) geçmişi izleyici ve yöneticisi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("watch", help="Panoyu izlemeye başla")

    list_parser = subparsers.add_parser("list", help="Geçmişi listele")
    list_parser.add_argument("--limit", type=int, default=20, help="Gösterilecek girdi sayısı")

    search_parser = subparsers.add_parser("search", help="Geçmişte metin ara")
    search_parser.add_argument("query", type=str, help="Aranacak metin")

    copy_parser = subparsers.add_parser("copy", help="Bir girdiyi panoya geri kopyala")
    copy_parser.add_argument("id", type=int, help="Girdi ID'si")

    show_parser = subparsers.add_parser("show", help="Bir girdinin tam içeriğini göster")
    show_parser.add_argument("id", type=int, help="Girdi ID'si")

    subparsers.add_parser("clear", help="Tüm geçmişi temizle")

    args = parser.parse_args()

    if args.command == "watch":
        watch()
    elif args.command == "list":
        list_entries(args.limit)
    elif args.command == "search":
        search_entries(args.query)
    elif args.command == "copy":
        copy_entry(args.id)
    elif args.command == "show":
        show_entry(args.id)
    elif args.command == "clear":
        clear_history()


if __name__ == "__main__":
    main()
