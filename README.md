<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/wordmark/geektype-wordmark-dark.svg">
    <img src="assets/wordmark/geektype-wordmark-light.svg" alt="GeekType" width="260">
  </picture>
</p>

<p align="center" dir="rtl">ابزار لینوکسی که متنِ تایپ‌شده با زبان اشتباه صفحه‌کلید را با کلید <bdi>F9</bdi>، در هر برنامه‌ای، به فارسی یا انگلیسی درست تبدیل می‌کند.</p>
<p align="center">A Linux tool that fixes text typed in the wrong keyboard layout, Persian or English, with the F9 key, in any app.</p>

<p align="center"><a href="https://mani-imani.github.io/GeekType/"><b>mani-imani.github.io/GeekType</b></a></p>
<p align="center"><a href="#فارسی">فارسی</a> · <a href="#english">English</a> · <code>v2.0.0</code></p>

---

<div dir="rtl">

## فارسی

### چه کاری می‌کند
وقتی یادتان رفته زبان صفحه‌کلید را عوض کنید و به‌جای «سلام» نوشته‌اید <code dir="ltr">sghl</code>، کافی است متن را انتخاب کنید و <bdi>F9</bdi> را بزنید.

1. متنی را که با چیدمان اشتباه نوشته شده، در هر برنامه‌ای انتخاب کنید.
2. کلید <bdi>F9</bdi> را بزنید.
3. متن انتخاب‌شده با نسخه‌ی درست جایگزین می‌شود و کلیپ‌بورد قبلی‌تان برمی‌گردد.

هر حرف به حرفی تبدیل می‌شود که همان کلید فیزیکی در چیدمان دیگر می‌دهد. جهت تبدیل (فارسی به انگلیسی یا برعکس) را خود ابزار تشخیص می‌دهد. جدول کلیدها با فایل رسمی چیدمان فارسی اوبونتو (<code dir="ltr">xkb</code>) تطبیق داده شده است. نیم‌فاصله، نشانه‌ها و رقم‌ها هم تبدیل می‌شوند و اگر <bdi>Caps Lock</bdi> روشن بوده، جبران می‌شود.

این نسخه فقط لینوکس را پوشش می‌دهد. همین ابزار در آینده برای ویندوز هم ساخته می‌شود، ولی هنوز زمانی برای آن تعیین نشده است.

### الزام‌ها
- اوبونتو با <bdi>GNOME</bdi> و <bdi>Wayland</bdi>. فقط همین ترکیب آزموده شده است.
- بسته‌های <code dir="ltr">wl-clipboard</code>، <code dir="ltr">ydotool</code> و <code dir="ltr">libnotify-bin</code>. فرمان نصب آن‌ها را نصب می‌کند.

### نصب
**از AppImage:** فایل <code dir="ltr">GeekType-x86_64.AppImage</code> را از [صفحه‌ی نسخه‌ها](https://github.com/mani-imani/GeekType/releases) بگیرید و اجرا کنید:

<div dir="ltr">

```bash
chmod +x GeekType-x86_64.AppImage
./GeekType-x86_64.AppImage --install
```

</div>

فرمان نصب برای نصب بسته‌ها و ساخت سرویس <code dir="ltr">ydotoold</code> رمز کاربر (<code dir="ltr">sudo</code>) را می‌خواهد. میان‌بر <bdi>F9</bdi> هم در تنظیمات <bdi>GNOME</bdi> ثبت می‌شود. اگر <bdi>AppImage</bdi> اجرا نشد، بسته‌ی <code dir="ltr">libfuse2</code> را نصب کنید.

**از سورس:** فقط به <bdi>Python 3.8</bdi> یا بالاتر نیاز است.

<div dir="ltr">

```bash
git clone https://github.com/mani-imani/GeekType.git
cd GeekType
python3 bin/geektype --install
```

</div>

### فرمان‌ها
| فرمان | کار |
| --- | --- |
| <code dir="ltr">geektype</code> | متن انتخاب‌شده را اصلاح می‌کند (همان کاری که <bdi>F9</bdi> می‌کند) |
| <code dir="ltr">geektype --install</code> | بسته‌ها، سرویس، آیکون و میان‌بر <bdi>F9</bdi> را نصب می‌کند |
| <code dir="ltr">geektype --doctor</code> | هر بخش را بررسی می‌کند و مشکل را می‌گوید |
| <code dir="ltr">geektype --convert "sghl"</code> | فقط متن را تبدیل و چاپ می‌کند، بدون دست زدن به دسکتاپ |
| <code dir="ltr">geektype --uninstall</code> | میان‌بر و سرویس را حذف می‌کند |

فایل گزارش: <code dir="ltr">~/.local/state/geektype/geektype.log</code> (فقط تعداد حروف اصلاح‌شده ثبت می‌شود، نه خود متن).

### اگر کار نکرد
<code dir="ltr">geektype --doctor</code> را اجرا کنید. این فرمان بسته‌ها، سرویس، سوکت، فرستادن کلید، کلیپ‌بورد و میان‌بر را یکی‌یکی بررسی می‌کند. اگر نسخه‌ی ۱ نصب بوده، <code dir="ltr">--install</code> سرویس قدیمی آن را برمی‌دارد.

### توسعه
<div dir="ltr">

```bash
python3 -m unittest discover -s tests -v
./packaging/build_appimage.sh
```

</div>

صفحه‌ی محصول در پوشه‌ی <code dir="ltr">docs/</code> است (فارسی و انگلیسی). با زدن یک برچسب نسخه (مثل <code dir="ltr">v2.0.0</code>)، <bdi>GitHub Actions</bdi> آزمون‌ها را اجرا می‌کند، <bdi>AppImage</bdi> را می‌سازد و به همان نسخه پیوست می‌کند.

### مجوز
<bdi>MIT</bdi>. فایل [LICENSE](LICENSE) را ببینید. آیکون‌های صفحه‌ی محصول از <bdi>Bootstrap Icons</bdi> (<bdi>MIT</bdi>) و فونت‌ها با مجوز <bdi>SIL OFL</bdi> هستند.

### نسخه
<code dir="ltr">v2.0.0</code> · تاریخچه در [CHANGELOG.md](CHANGELOG.md).

</div>

---

## English

### What it does
When you forget to switch the keyboard layout and type `sghl` instead of the Persian word for hello, select the text and press F9.

1. In any app, select the text that was typed in the wrong layout.
2. Press F9.
3. The selection is replaced with the fixed text and your previous clipboard is put back.

Each character becomes the one the same physical key gives in the other layout. GeekType works out the direction (Persian to English or the other way) by itself. The key table was checked against Ubuntu's official Persian layout file (`xkb`). Half-spaces, symbols and digits convert too, and an accidental Caps Lock is undone.

This release covers Linux only. The same tool will be built for Windows in the future; there is no date yet.

### Requirements
- Ubuntu with GNOME on Wayland. Only this combination has been tried.
- The packages `wl-clipboard`, `ydotool` and `libnotify-bin`. The install command sets them up.

### Install
**From the AppImage:** get `GeekType-x86_64.AppImage` from the [releases page](https://github.com/mani-imani/GeekType/releases) and run:

```bash
chmod +x GeekType-x86_64.AppImage
./GeekType-x86_64.AppImage --install
```

The install command asks for your password (`sudo`) to install packages and create the `ydotoold` service. It also registers the F9 shortcut in GNOME settings. If the AppImage does not start, install `libfuse2`.

**From source:** only Python 3.8 or newer is needed.

```bash
git clone https://github.com/mani-imani/GeekType.git
cd GeekType
python3 bin/geektype --install
```

### Commands
| Command | What it does |
| --- | --- |
| `geektype` | fixes the selected text (what F9 does) |
| `geektype --install` | installs packages, the service, the icon and the F9 shortcut |
| `geektype --doctor` | checks every part and tells you what is wrong |
| `geektype --convert "sghl"` | only converts and prints the text, without touching the desktop |
| `geektype --uninstall` | removes the shortcut and the service |

Log file: `~/.local/state/geektype/geektype.log` (only the number of characters fixed is logged, never the text).

### If it does not work
Run `geektype --doctor`. It checks the packages, the service, the socket, key sending, the clipboard and the shortcut one by one. If v1 was installed, `--install` removes its old service.

### Development
```bash
python3 -m unittest discover -s tests -v
./packaging/build_appimage.sh
```

The product page lives in `docs/` (Persian and English). Pushing a version tag (such as `v2.0.0`) makes GitHub Actions run the tests, build the AppImage and attach it to that release.

### License
MIT, see [LICENSE](LICENSE). Product-page icons are Bootstrap Icons (MIT); fonts are under the SIL OFL.

### Version
`v2.0.0` · see [CHANGELOG.md](CHANGELOG.md).

---

<p align="center"><a href="https://github.com/mani-imani"><b>by GeekMani</b></a> · <a href="https://github.com/mani-imani">از گیک‌مانی</a> · <a href="https://maniimani.ir">maniimani.ir</a></p>
