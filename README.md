# 📋 Clipboard History

Sistem panosunu (clipboard) arka planda izleyip her yeni kopyalanan
metni yerel bir SQLite veritabanında saklayan araç. Daha sonra geçmişte
arama yapabilir ve istediğiniz bir girdiyi tekrar panoya
kopyalayabilirsiniz — işletim sisteminizin yerleşik pano geçmişi yoksa
ya da daha uzun bir geçmiş istiyorsanız kullanışlıdır.

## Özellikler

- 🔄 Panoyu periyodik olarak izler, her değişikliği otomatik kaydeder
- 💾 Yerel SQLite veritabanı (`~/.clipboard_history.db`) — bulut yok, tamamen yerel
- 🔍 Geçmişte serbest metin arama
- 📋 Eski bir girdiyi tek komutla tekrar panoya kopyalama
- 🧹 Geçmişi tamamen temizleme seçeneği

## Kurulum

```bash
pip install -r requirements.txt
```

> **Linux kullanıcıları:** `pyperclip` panoya erişmek için bir sistem
> aracına ihtiyaç duyar. Eğer "copy/paste mechanism not found" hatası
> alırsanız: `sudo apt-get install xclip` (X11) veya
> `sudo apt-get install wl-clipboard` (Wayland) kurun.

## Kullanım

```bash
# Arka planda izlemeye başla (terminali açık tutun veya tmux/screen kullanın)
python3 clip_history.py watch

# Son 20 girdiyi listele
python3 clip_history.py list

# Son 50 girdiyi listele
python3 clip_history.py list --limit 50

# Geçmişte ara
python3 clip_history.py search "fatura"

# Bir girdinin tam içeriğini gör
python3 clip_history.py show 5

# Bir girdiyi panoya geri kopyala
python3 clip_history.py copy 5

# Tüm geçmişi temizle (onay istenir)
python3 clip_history.py clear
```

## Gizlilik notu

Bu araç **tamamen yerel** çalışır — hiçbir veri internete gönderilmez.
Veritabanı sadece kendi bilgisayarınızda, `~/.clipboard_history.db`
dosyasında tutulur. Ancak şifre gibi hassas bilgileri kopyaladığınızda
bunlar da düz metin olarak bu dosyaya kaydedileceğini unutmayın —
hassas bilgi kopyaladıktan sonra `clear` komutuyla geçmişi temizlemeyi
düşünebilirsiniz.

## Lisans

MIT
