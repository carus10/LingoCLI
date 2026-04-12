# LingoCLI Çoklu Çalışma Alanı (Workspace) Özelliği

Mevcut durumda LingoCLI komutları uygulamanın çalıştığı varsayılan bilgisayar konumunda yürütüyor ve her oturum kapatıldığında hafıza sıfırlanıyor (veya tek bir session devam ediyor ve proje bazlı ayrılmıyor).
Önerilen bu plan ile kullanıcılar 3 farklı projeye kadar çalışma alanı belirleyebilecek, her projenin kendi geçmiş hafızası dondurularak kaydedilecek ve komutlar doğrudan projenin dizininde (`cwd`) çalıştırılacak.

## User Review Required

> [!IMPORTANT]
> Bu eklemeler UI ve core mantıkta değişiklik gerektiriyor. Yeni özelliklerin akışı şu şekildedir:
> 1. Header (üst çubuk) bölümüne "📁 Projeler" (Workspaces) butonu ve bir açılır menü (veya modal pencere) eklenecektir.
> 2. LingoCLI'yi başlattığınızda önceden bir projeniz varsa onu seçerek eski anılarla devam edebilirsiniz.
> 3. `tkinter.filedialog` kullanılarak proje klasörleri seçtirilecek.
> Lütfen plandaki kurguyu inceleyip onay verin.

## Proposed Changes

---
### UI ve Mantık Güncellemeleri (ai_terminal_asistan.py)
Bu dosyada Workspace UI elemanları, `cwd` destekli komut çalıştırma ve Workspace hafıza kaydetme/yükleme fonksiyonları yazılacaktır.

#### [MODIFY] [ai_terminal_asistan.py](file:///c:/Users/taska/Desktop/LingoCLI/ai_terminal_asistan.py)
- `workspaces.json` veritabanını okuma/yazma fonksiyonları eklenecek.
- `AITerminalAsistani` sınıfına `aktif_workspace` değişkeni ve workspace değiştirme metodları (örn. `_workspace_degistir`, `_workspace_kaydet`) eklenecek.
- `_baslik_cubugu` içerisine "📁 Projeler" butonu eklenecek.
- Butona basıldığında 3 slotlu bir seçim penceresi (CTkToplevel) ile var olanları seçme veya yeni klasör (`askdirectory`) ekleme imkanı sağlanacak.
- `_giris_satiri` kısmında yer alan "PS > " metni, seçili projenin ismine göre (Örn: `E-Ticaret > `) dinamik güncellenecek.
- `komutu_calistir` fonksiyonu `cwd` (current working directory) parametresi alacak şekilde güncellenecek. Seçtiğiniz projenin yolunda poweshell komutları yürütülecek.

---
### Çeviri / Dil Güncellemeleri (dil.py)
Yeni kullanılacak UI elementlerinin (Projeler, Çalışma Alanı Seç, Yeni Klasör, Boş Slot vs.) TR/EN çevirileri eklenecek.

#### [MODIFY] [dil.py](file:///c:/Users/taska/Desktop/LingoCLI/dil.py)
- `btn_workspaces`: "📁 Projeler" / "📁 Workspaces"
- `workspace_title`: "Çalışma Alanları" / "Workspaces"
- `workspace_empty`: "[Boş Slot - Yeni Seç]" / "[Empty - Select New]"
- `workspace_active`: "[Aktif]" / "[Active]"
- `workspace_clear`: "Kaldır" / "Clear"

## Open Questions

> [!WARNING]
> Öğrenmek istediğim bir detay: Slotlardan bir projeyi "Kaldır" (Clear) seçeneği eklemeli miyiz, yoksa sadece üzerine tıklayıp yeni klasör seçmek yeterli mi? (Plana şimdilik bir 'Kaldır/Temizle' butonu da eklemeyi öngördüm ki slotu boşaltmak istenebilir).
> 3 proje sınırı sabit kalacak, doğru mu?

## Verification Plan

### Automated Tests
- PyInstaller aracılığı ile exe (Windows yürütülebilir dosyası) inşası (build) testi kontrol edilecek. Komut: `pyinstaller AI_Terminal.spec`.

### Manual Verification
1. LingoCLI açılacak. "Projeler" butonuna tıklanıp `TestProje1` adında bir klasör seçilecek.
2. Terminal input kısmında `TestProje1 >` prompt'u görülecek.
3. Bu projede `mkdir yeni_klasor` gibi bir komut verilip, klasörün masaüstüne falan değil direkt hedef `TestProje1` klasörünün içine oluştuğu teyit edilecek.
4. İkinci bir `TestProje2` klasörü seçilip, projeler arası geçişte her projenin son hafızasının kaydolduğu, yeni projeye geçince modelin eski bağlamda kaldığı (`workspaces.json` verisi) test edilecek.
5. Kullanıcıya final .exe dosyası `dist/` klasörü içinde sunulacak.
