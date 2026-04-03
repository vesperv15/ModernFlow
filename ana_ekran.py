import sys
import json
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
                            QGraphicsTextItem, QGraphicsPolygonItem, QMenu, QGraphicsLineItem, 
                            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QGraphicsEllipseItem, QGraphicsItem,
                            QLineEdit, QTextEdit, QLabel, QColorDialog, QFontDialog, 
                            QFrame, QAction, QToolBar, QSlider, QSizePolicy, QInputDialog, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt, QPointF, QLineF, QSize, QPoint, QTimer
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QPainter, QPolygonF, QPixmap, QIcon, QPolygon 

# BAĞLANTI ÇİZGİSİ
class Baglanticizgisi(QGraphicsLineItem):
    def __init__(self, baslangic, bitis, etiket=""):
        super().__init__()
        self.baslangic, self.bitis = baslangic, bitis
        self.setPen(QPen(QColor("#ffffff"), 2))
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)
        self.etiket_item = QGraphicsTextItem(etiket, self)
        renk = "#00ff00" if etiket == "Evet" else "#ff4444" if etiket == "Hayır" else "white"
        self.etiket_item.setDefaultTextColor(QColor(renk))
        self.etiket_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.guncelle()

    def guncelle(self):
        if not self.baslangic.scene() or not self.bitis.scene(): return
        p1, p2 = self.baslangic.sceneBoundingRect().center(), self.bitis.sceneBoundingRect().center()
        self.setLine(QLineF(p1, p2))
        mid = (p1 + p2) / 2
        self.etiket_item.setPos(mid.x() + 5, mid.y() - 15)

    def sil(self, scene):
        if self in self.baslangic.baglantilar: self.baslangic.baglantilar.remove(self)
        if self in self.bitis.baglantilar: self.bitis.baglantilar.remove(self)
        if self.scene(): scene.removeItem(self)

#BLOK YETENEKLERİ
class BlokYetenekleri:
    def __init__(self, tip_adi):
        self.baglantilar = []
        self.tip_adi = tip_adi 
        self.normal_renk = None
        self.nesne_adi = f"{tip_adi}_{id(self) % 10000}"
        self.degisken = ""
        self.islem = ""
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for b in self.baglantilar: b.guncelle()
        return super().itemChange(change, value)

    def sil(self, scene):
        for c in list(self.baglantilar): c.sil(scene)
        self.baglantilar.clear()
        if self.scene(): scene.removeItem(self)

    def parlat(self, durum=True):
        if durum:
            if not self.normal_renk: self.normal_renk = self.brush().color()
            self.setBrush(QBrush(QColor("#ffcc00")))
            self.setPen(QPen(Qt.white, 4))
        else:
            if self.normal_renk:
                self.setBrush(QBrush(self.normal_renk))
                self.setPen(QPen(Qt.white, 2))

#BLOK SINIFLARI
class BaslatDurdurBlogu(BlokYetenekleri, QGraphicsEllipseItem):
    def __init__(self, x, y, metin, renk, tip):
        QGraphicsEllipseItem.__init__(self, 0, 0, 140, 50)
        BlokYetenekleri.__init__(self, tip)
        self.setPos(x, y); self.setBrush(QBrush(QColor(renk))); self.setPen(QPen(Qt.white, 2))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsGeometryChanges)
        self.yazi = QGraphicsTextItem(metin, self); self.yazi.setDefaultTextColor(Qt.white); self.ortala()
    def ortala(self):
        r, t = self.boundingRect(), self.yazi.boundingRect()
        self.yazi.setPos((r.width()-t.width())/2, (r.height()-t.height())/2)

class IslemDegiskenBlogu(BlokYetenekleri, QGraphicsRectItem):
    def __init__(self, x, y, metin, renk, tip):
        QGraphicsRectItem.__init__(self, 0, 0, 150, 55)
        BlokYetenekleri.__init__(self, tip)
        self.setPos(x, y); self.setBrush(QBrush(QColor(renk))); self.setPen(QPen(Qt.white, 2))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsGeometryChanges)
        self.yazi = QGraphicsTextItem(metin, self); self.yazi.setDefaultTextColor(Qt.white); self.ortala()
    def ortala(self):
        r, t = self.boundingRect(), self.yazi.boundingRect()
        self.yazi.setPos((r.width()-t.width())/2, (r.height()-t.height())/2)

class KararBlogu(BlokYetenekleri, QGraphicsPolygonItem):
    def __init__(self, x, y, metin):
        poly = QPolygonF([QPointF(75, 0), QPointF(150, 35), QPointF(75, 70), QPointF(0, 35)])
        QGraphicsPolygonItem.__init__(self, poly)
        BlokYetenekleri.__init__(self, "EĞER")
        self.setPos(x, y); self.setBrush(QBrush(QColor("#ff9f0a"))); self.setPen(QPen(Qt.white, 2))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsGeometryChanges)
        self.yazi = QGraphicsTextItem(metin, self); self.yazi.setDefaultTextColor(Qt.white); self.ortala()
    def ortala(self):
        r, t = self.boundingRect(), self.yazi.boundingRect()
        self.yazi.setPos((r.width()-t.width())/2, (r.height()-t.height())/2)

class GirisCikisBlogu(BlokYetenekleri, QGraphicsPolygonItem):
    def __init__(self, x, y, metin, renk, tip):
        poly = QPolygonF([QPointF(20, 0), QPointF(160, 0), QPointF(140, 50), QPointF(0, 50)])
        QGraphicsPolygonItem.__init__(self, poly)
        BlokYetenekleri.__init__(self, tip)
        self.setPos(x, y); self.setBrush(QBrush(QColor(renk))); self.setPen(QPen(Qt.white, 2))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsGeometryChanges)
        self.yazi = QGraphicsTextItem(metin, self); self.yazi.setDefaultTextColor(Qt.white); self.ortala()
    def ortala(self):
        r, t = self.boundingRect(), self.yazi.boundingRect()
        self.yazi.setPos((r.width()-t.width())/2, (r.height()-t.height())/2)

class DugumBlogu(BlokYetenekleri, QGraphicsEllipseItem):
    def __init__(self, x, y):
        QGraphicsEllipseItem.__init__(self, 0, 0, 25, 25)
        BlokYetenekleri.__init__(self, "DÜĞÜM")
        self.setPos(x, y); self.setBrush(QBrush(QColor("#8e8e93"))); self.setPen(QPen(Qt.white, 2))
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsGeometryChanges)
        self.yazi = QGraphicsTextItem("", self)

class AkisView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene)
        self.parent_app = parent
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsTextItem): item = item.parentItem()
        menu = QMenu(); menu.setStyleSheet("background:#2e2e3e; color:white;")
        if item:
            if isinstance(item, Baglanticizgisi):
                menu.addAction("✂️ Kes").triggered.connect(lambda: item.sil(self.scene()))
            else:
                if not self.parent_app.secili_baslangic:
                    menu.addAction("🔗 Bağlantıyı Başlat").triggered.connect(lambda: self.parent_app.baglanti_sec(item))
                else:
                    menu.addAction("🎯 Buraya Bağla").triggered.connect(lambda: self.parent_app.baglanti_kur(item))
                menu.addAction("🗑️ Sil").triggered.connect(lambda: self.parent_app.blok_sil(item))
        menu.exec_(event.globalPos())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.scene().selectedItems():
                if isinstance(item, QGraphicsTextItem) and item.parentItem():
                    item = item.parentItem()
                if hasattr(item, 'sil'):
                    item.sil(self.scene())
                    if self.parent_app.secili_baslangic == item:
                        self.parent_app.secili_baslangic = None
        super().keyPressEvent(event)

# ANA UYGULAMA
class ModernFlowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Flow v5.3 - Dosya Kayıt Sistemi")
        self.resize(1400, 950)
        self.setStyleSheet("background-color:#1e1e2e; color:white; font-family:'Segoe UI';")
        
        self.renk_penceresi = QColorDialog(self)
        self.renk_penceresi.setOptions(QColorDialog.NoButtons | QColorDialog.DontUseNativeDialog)
        self.renk_penceresi.currentColorChanged.connect(self.canli_renk_uygula)

        self.setup_ui_core()
        
        ana_widget = QWidget(); self.setCentralWidget(ana_widget)
        ana_lay = QHBoxLayout(ana_widget)
        
        # SOL PANEL
        sol_panel = QWidget(); sol_panel.setFixedWidth(200); sol_lay = QVBoxLayout(sol_panel)
        sol_panel.setStyleSheet("background:#252535; border-right:1px solid #3d3d4d;")
        sol_lay.addWidget(QLabel("<b>📦 ARAÇLAR</b>"))
        btns = [("BAŞLAT", "#34c759"), ("İŞLEM", "#5e5ce6"), ("DEĞİŞKEN", "#af52de"), ("EĞER", "#ff9f0a"), 
                ("GİRİŞ", "#30d158"), ("ÇIKIŞ", "#32ade6"), ("DURDUR", "#ff3b30"), ("DÜĞÜM", "#8e8e93")]
        for m, r in btns:
            btn = QPushButton(); btn.setIcon(self.ikon_olustur(m, r)); btn.setIconSize(QSize(160, 70))
            btn.setStyleSheet("QPushButton{background:transparent; border:none; margin:3px;} QPushButton:hover{background:#3d3d4d; border-radius:10px;}")
            btn.clicked.connect(lambda ch, tip=m: self.blok_ekle(tip))
            sol_lay.addWidget(btn)
        sol_lay.addStretch()
        
        # ORTA BÖLÜM
        orta_panel = QWidget(); orta_lay = QVBoxLayout(orta_panel)
        self.scene = QGraphicsScene(); self.scene.setBackgroundBrush(QColor("#1e1e2e"))
        self.view = AkisView(self.scene, self)
        self.scene.selectionChanged.connect(self.secim_degisti)
        orta_lay.addWidget(self.view, 7)
        
        orta_lay.addWidget(QLabel("<b>💻 ALGORİTMA TERMİNALİ</b>"))
        self.terminal = QTextEdit(); self.terminal.setReadOnly(True); self.terminal.setFixedHeight(120)
        self.terminal.setStyleSheet("background:#000; color:#00ff00; font-family:'Consolas'; border:1px solid #3d3d4d;")
        orta_lay.addWidget(self.terminal, 2)
        
        # SAĞ PANEL
        sag_panel = QWidget(); sag_panel.setFixedWidth(280); sag_lay = QVBoxLayout(sag_panel)
        sag_panel.setStyleSheet("background:#252535; border-left:1px solid #3d3d4d;")
        
        sag_lay.addWidget(QLabel("<b>NESNE ÖZELLİKLERİ</b>"))
        sag_lay.addSpacing(10)
        
        sag_lay.addWidget(QLabel("<span style='color: #8e8e93; font-size: 9pt;'>Nesne Adı</span>"))
        self.nesne_adi_lbl = QLabel("-")
        self.nesne_adi_lbl.setStyleSheet("padding:5px; background:#1e1e2e; border:1px solid #3d3d4d; color:#34c759; font-weight:bold;")
        sag_lay.addWidget(self.nesne_adi_lbl)
        
        sag_lay.addWidget(QLabel("<span style='color: #8e8e93; font-size: 9pt;'>Görüntülenecek Metin</span>"))
        self.goruntu_metin_edit = QTextEdit()
        self.goruntu_metin_edit.setFixedHeight(60)
        self.goruntu_metin_edit.setStyleSheet("padding:5px; background:#1e1e2e; border:1px solid #3d3d4d; color:white;")
        self.goruntu_metin_edit.textChanged.connect(self.yazi_guncelle)
        sag_lay.addWidget(self.goruntu_metin_edit)
        
        sag_lay.addWidget(QLabel("<span style='color: #8e8e93; font-size: 9pt;'>Gösterilecek/Alınacak Değişken</span>"))
        self.degisken_edit = QLineEdit()
        self.degisken_edit.setStyleSheet("padding:5px; background:#1e1e2e; border:1px solid #3d3d4d; color:white;")
        self.degisken_edit.textChanged.connect(self.degisken_guncelle)
        sag_lay.addWidget(self.degisken_edit)
        
        sag_lay.addWidget(QLabel("<span style='color: #8e8e93; font-size: 9pt;'>Yapılacak İşlem / Şart</span>"))
        self.islem_edit = QTextEdit()
        self.islem_edit.setFixedHeight(60)
        self.islem_edit.setStyleSheet("padding:5px; background:#1e1e2e; border:1px solid #3d3d4d; color:#af52de; font-family:'Consolas';")
        self.islem_edit.textChanged.connect(self.islem_guncelle)
        sag_lay.addWidget(self.islem_edit)
        
        sag_lay.addSpacing(20)
        sag_lay.addWidget(QLabel("<b>🎨 GÖRÜNÜM</b>"))
        btn_renk = QPushButton("🎨 Blok Rengi"); btn_renk.clicked.connect(lambda: self.renk_penceresi.show())
        btn_font = QPushButton("Aa Font Seç"); btn_font.clicked.connect(self.font_secici_ac)
        btn_y_renk = QPushButton("🖌️ Yazı Rengi"); btn_y_renk.clicked.connect(self.yazi_rengi_sec)
        for b in [btn_renk, btn_font, btn_y_renk]:
            b.setStyleSheet("background:#3d3d4d; padding:8px; border-radius:5px; text-align:left; padding-left:10px;")
            sag_lay.addWidget(b)

        sag_lay.addSpacing(30)
        sag_lay.addWidget(QLabel("<b>🐞 BUG / UYARI KONSOLU</b>"))
        self.bug_log = QTextEdit(); self.bug_log.setReadOnly(True); self.bug_log.setFixedHeight(120)
        self.bug_log.setStyleSheet("background:#111; color:#ff4444; font-family:'Consolas'; border-radius:4px; border:1px solid #ff4444;")
        sag_lay.addWidget(self.bug_log); sag_lay.addStretch()
        
        ana_lay.addWidget(sol_panel); ana_lay.addWidget(orta_panel, 5); ana_lay.addWidget(sag_panel)
        
        self.secili_baslangic = None
        self.current_sim_block = None
        self.degiskenler = {}
        self.sim_timer = QTimer(); self.sim_timer.timeout.connect(self.sim_adim_at)
        self.sim_time = 0

    def setup_ui_core(self):
        bagla_act = QAction(self); bagla_act.setShortcut("Alt+B"); bagla_act.triggered.connect(self.baglanti_kisayolu_tetikle)
        self.addAction(bagla_act)

        self.toolbar = QToolBar(); self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setStyleSheet("background:#2d2d3d; spacing:15px; padding:5px; border-bottom:2px solid #3d3d4d;")
        
        # KAYDET VE AÇ BUTONLARI EKLENDİ
        self.btn_load = self.add_sim_btn("📂", "Projeyi Aç", self.projeyi_ac)
        self.btn_save = self.add_sim_btn("💾", "Projeyi Kaydet", self.projeyi_kaydet)
        self.toolbar.addSeparator()
        
        self.label_sure = QLabel("Süre = 00:00"); self.toolbar.addWidget(self.label_sure)
        
        self.btn_play = self.add_sim_btn("▶️", "Başlat", self.sim_baslat)
        self.btn_pause = self.add_sim_btn("⏸️", "Durdur", self.sim_duraklat)
        self.btn_stop = self.add_sim_btn("⏹️", "Sıfırla", self.sim_sifirla)

        self.toolbar.addSeparator(); self.toolbar.addWidget(QLabel(" Hız: "))
        self.hiz_slider = QSlider(Qt.Horizontal); self.hiz_slider.setRange(200, 2000); self.hiz_slider.setValue(1000)
        self.hiz_slider.valueChanged.connect(lambda v: self.hiz_label.setText(f"{v} ms"))
        self.toolbar.addWidget(self.hiz_slider)
        self.hiz_label = QLabel("1000 ms"); self.toolbar.addWidget(self.hiz_label)

    def add_sim_btn(self, text, tool, func):
        b = QPushButton(text); b.setToolTip(tool); b.clicked.connect(func)
        b.setStyleSheet("background:#3d3d4d; border-radius:5px; padding:8px; font-size:12pt;")
        self.toolbar.addWidget(b); return b

    #DOSYA KAYDETME VE AÇMA İŞLEMLERİ
    def projeyi_kaydet(self):
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "Projeyi Kaydet", "", "Modern Flow Dosyası (*.mflow);;JSON Dosyası (*.json)")
        if not dosya_yolu: return

        veri = {"bloklar": [], "baglantilar": []}

        for item in self.scene.items():
            if isinstance(item, BlokYetenekleri):
                blok_data = {
                    "tip": item.tip_adi,
                    "x": item.x(),
                    "y": item.y(),
                    "nesne_adi": item.nesne_adi,
                    "metin": item.yazi.toPlainText(),
                    "degisken": getattr(item, 'degisken', ''),
                    "islem": getattr(item, 'islem', ''),
                    "renk": item.brush().color().name()
                }
                veri["bloklar"].append(blok_data)

        for item in self.scene.items():
            if isinstance(item, Baglanticizgisi):
                baglanti_data = {
                    "baslangic": item.baslangic.nesne_adi,
                    "bitis": item.bitis.nesne_adi,
                    "etiket": item.etiket_item.toPlainText()
                }
                veri["baglantilar"].append(baglanti_data)

        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
        
        self.terminal.append(f">> 💾 Proje başarıyla kaydedildi: {dosya_yolu}")

    def projeyi_ac(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(self, "Projeyi Aç", "", "Modern Flow Dosyası (*.mflow);;JSON Dosyası (*.json)")
        if not dosya_yolu: return

        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                veri = json.load(f)

            # Sahnede ne varsa temizle
            self.scene.clear()
            self.secili_baslangic = None
            self.current_sim_block = None
            self.degiskenler = {}

            blok_dict = {}

            # Blokları yeniden inşa et
            for b_data in veri.get("bloklar", []):
                tip = b_data["tip"]
                x, y = b_data["x"], b_data["y"]
                renk = b_data.get("renk", "#34c759")
                
                if tip == "BAŞLAT" or tip == "DURDUR": blok = BaslatDurdurBlogu(x, y, b_data.get("metin", ""), renk, tip)
                elif tip == "İŞLEM" or tip == "DEĞİŞKEN": blok = IslemDegiskenBlogu(x, y, b_data.get("metin", ""), renk, tip)
                elif tip == "EĞER": blok = KararBlogu(x, y, b_data.get("metin", ""))
                elif tip in ["GİRİŞ", "ÇIKIŞ"]: blok = GirisCikisBlogu(x, y, b_data.get("metin", ""), renk, tip)
                elif tip == "DÜĞÜM": blok = DugumBlogu(x, y)
                else: continue

                blok.nesne_adi = b_data["nesne_adi"]
                blok.degisken = b_data.get("degisken", "")
                blok.islem = b_data.get("islem", "")
                
                self.scene.addItem(blok)
                blok_dict[blok.nesne_adi] = blok

            # Çizgileri (bağlantıları) geri bağla
            for c_data in veri.get("baglantilar", []):
                bas_id = c_data["baslangic"]
                bit_id = c_data["bitis"]
                
                if bas_id in blok_dict and bit_id in blok_dict:
                    bas = blok_dict[bas_id]
                    hedef = blok_dict[bit_id]
                    c = Baglanticizgisi(bas, hedef, c_data.get("etiket", ""))
                    self.scene.addItem(c)
                    bas.baglantilar.append(c)
                    hedef.baglantilar.append(c)
                    c.guncelle() # Pozisyonu oturt

            self.terminal.append(f">> 📂 Proje başarıyla yüklendi: {dosya_yolu}")
        except Exception as e:
            self.hata_log(f"Dosya okuma hatası: {e}")

    #SİMÜLASYON VE DİĞER KODLAR
    def sim_baslat(self):
        self.degiskenler = {}
        self.btn_play.setStyleSheet("background: #34c759; color: black; border-radius:5px; padding:8px;")
        self.terminal.clear()
        self.terminal.append(">> Simülasyon başlatılıyor...")
        self.sim_timer.start(self.hiz_slider.value())

    def sim_duraklat(self):
        self.sim_timer.stop()
        self.btn_play.setStyleSheet("background: #3d3d4d; border-radius:5px; padding:8px;")
        self.terminal.append(">> Durduruldu.")

    def sim_sifirla(self):
        self.sim_timer.stop()
        if self.current_sim_block: self.current_sim_block.parlat(False)
        self.current_sim_block = None; self.sim_time = 0
        self.label_sure.setText("Süre = 00:00")
        self.btn_play.setStyleSheet("background: #3d3d4d; border-radius:5px; padding:8px;")
        self.terminal.append(">> Sistem sıfırlandı.")

    def sim_adim_at(self):
        if not self.current_sim_block:
            for item in self.scene.items():
                if isinstance(item, BaslatDurdurBlogu) and item.tip_adi == "BAŞLAT":
                    self.current_sim_block = item; break
            if not self.current_sim_block:
                self.hata_log("BAŞLAT bloğu bulunamadı!"); self.sim_timer.stop(); return

        self.current_sim_block.parlat(False)
        
        b = self.current_sim_block
        tip = b.tip_adi
        t_text = b.yazi.toPlainText()
        islem = b.islem.strip()
        degisken = b.degisken.strip()

        try:
            if tip in ["İŞLEM", "DEĞİŞKEN"]:
                if islem:
                    exec(islem, {}, self.degiskenler)
                    self.terminal.append(f">> [İŞLEM] {islem}")
                    
            elif tip == "GİRİŞ":
                self.sim_timer.stop()
                val, ok = QInputDialog.getText(self, "Algoritma Girişi", f"{t_text if t_text else 'Değer'}:")
                if ok:
                    try:
                        num_val = float(val)
                        if num_val.is_integer(): num_val = int(num_val)
                        self.degiskenler[degisken if degisken else "giris"] = num_val
                    except ValueError:
                        self.degiskenler[degisken if degisken else "giris"] = val
                    
                    self.terminal.append(f">> [GİRİŞ] {degisken if degisken else 'giris'} = {val}")
                    self.sim_timer.start(self.hiz_slider.value())
                else:
                    self.terminal.append(">> İptal edildi."); self.sim_sifirla(); return
                    
            elif tip == "ÇIKIŞ":
                if degisken and degisken in self.degiskenler:
                    cikis_val = self.degiskenler[degisken]
                    self.terminal.append(f">> [ÇIKIŞ] {t_text} {cikis_val}")
                elif islem:
                    cikis_val = eval(islem, {}, self.degiskenler)
                    self.terminal.append(f">> [ÇIKIŞ] {t_text} {cikis_val}")
                else:
                    self.terminal.append(f">> [ÇIKIŞ] {t_text}")
                    
        except Exception as e:
            self.hata_log(f"Matematiksel Hata ({tip}): {e}")
            self.sim_sifirla(); return

        cikanlar = [c for c in b.baglantilar if c.baslangic == b]
        if not cikanlar or tip == "DURDUR":
            self.terminal.append(">> ✅ Algoritma tamamlandı.")
            self.sim_timer.stop(); return
        
        if tip == "EĞER":
            try:
                if not islem: raise ValueError("EĞER bloğunda şart yazılmamış!")
                sart_sonucu = eval(islem, {}, self.degiskenler)
                hedef_etiket = "Evet" if sart_sonucu else "Hayır"
                hedef_baglanti = next((c for c in cikanlar if c.etiket_item.toPlainText() == hedef_etiket), cikanlar[0])
                self.current_sim_block = hedef_baglanti.bitis
                self.terminal.append(f">> [KARAR] {islem} -> {hedef_etiket}")
            except Exception as e:
                self.hata_log(f"EĞER Şart Hatası: {e}"); self.sim_sifirla(); return
        else:
            self.current_sim_block = cikanlar[0].bitis
        
        self.current_sim_block.parlat(True)
        self.view.centerOn(self.current_sim_block)
        
        self.sim_time += 1; m, s = divmod(self.sim_time, 60)
        self.label_sure.setText(f"Süre = {m:02d}:{s:02d}")

    #EDİTÖR GÜNCELLEMELERİ
    def secim_degisti(self):
        secili = self.scene.selectedItems()
        if secili and len(secili) == 1 and hasattr(secili[0], 'tip_adi'):
            b = secili[0]
            self.nesne_adi_lbl.setText(b.nesne_adi)
            
            self.goruntu_metin_edit.blockSignals(True)
            self.goruntu_metin_edit.setPlainText(b.yazi.toPlainText())
            self.goruntu_metin_edit.blockSignals(False)
            self.goruntu_metin_edit.setEnabled(True)
            
            self.degisken_edit.blockSignals(True)
            self.degisken_edit.setText(b.degisken)
            self.degisken_edit.blockSignals(False)
            self.degisken_edit.setEnabled(True)
                
            self.islem_edit.blockSignals(True)
            self.islem_edit.setPlainText(b.islem)
            self.islem_edit.blockSignals(False)
            self.islem_edit.setEnabled(True)
        else:
            self.nesne_adi_lbl.setText("-")
            self.goruntu_metin_edit.clear(); self.goruntu_metin_edit.setEnabled(False)
            self.degisken_edit.clear(); self.degisken_edit.setEnabled(False)
            self.islem_edit.clear(); self.islem_edit.setEnabled(False)

    def yazi_guncelle(self):
        secili = self.scene.selectedItems()
        if secili and len(secili) == 1 and hasattr(secili[0], 'yazi'):
            secili[0].yazi.setPlainText(self.goruntu_metin_edit.toPlainText())
            if hasattr(secili[0], 'ortala'): secili[0].ortala()

    def degisken_guncelle(self):
        secili = self.scene.selectedItems()
        if secili and len(secili) == 1 and hasattr(secili[0], 'degisken'):
            secili[0].degisken = self.degisken_edit.text()

    def islem_guncelle(self):
        secili = self.scene.selectedItems()
        if secili and len(secili) == 1 and hasattr(secili[0], 'islem'):
            secili[0].islem = self.islem_edit.toPlainText()

    def baglanti_kisayolu_tetikle(self):
        secili = self.scene.selectedItems()
        if secili and hasattr(secili[0], 'baglantilar'):
            if not self.secili_baslangic: self.secili_baslangic = secili[0]
            else: self.baglanti_kur(secili[0])

    def yazi_rengi_sec(self):
        r = QColorDialog.getColor()
        if r.isValid():
            for b in self.scene.selectedItems():
                if hasattr(b, 'yazi'): b.yazi.setDefaultTextColor(r)

    def canli_renk_uygula(self, r):
        for b in self.scene.selectedItems():
            if hasattr(b, 'setBrush'): b.setBrush(QBrush(r))

    def font_secici_ac(self):
        f, ok = QFontDialog.getFont()
        if ok:
            for b in self.scene.selectedItems():
                if hasattr(b, 'yazi'): b.yazi.setFont(f); b.ortala()

    def ikon_olustur(self, tip, renk):
        pix = QPixmap(160, 70); pix.fill(Qt.transparent); ptr = QPainter(pix)
        ptr.setRenderHint(QPainter.Antialiasing); ptr.setBrush(QBrush(QColor(renk))); ptr.setPen(QPen(Qt.white, 2))
        if tip in ["BAŞLAT", "DURDUR"]: ptr.drawEllipse(5, 5, 145, 55)
        elif tip in ["İŞLEM", "DEĞİŞKEN"]: ptr.drawRect(5, 5, 145, 55)
        elif tip == "EĞER": ptr.drawPolygon(QPolygon([QPoint(80, 5), QPoint(155, 35), QPoint(80, 65), QPoint(5, 35)]))
        elif tip in ["GİRİŞ", "ÇIKIŞ"]: ptr.drawPolygon(QPolygon([QPoint(25, 10), QPoint(155, 10), QPoint(135, 60), QPoint(5, 60)]))
        elif tip == "DÜĞÜM": ptr.drawEllipse(65, 20, 30, 30)
        if tip != "DÜĞÜM":
            ptr.setPen(Qt.white); ptr.setFont(QFont("Segoe UI", 9, QFont.Bold)); ptr.drawText(pix.rect(), Qt.AlignCenter, tip)
        ptr.end(); return QIcon(pix)

    def hata_log(self, mesaj): self.bug_log.append(f"> ❌ {mesaj}")

    def blok_ekle(self, tip):
        p = self.view.mapToScene(100, 100)
        if tip == "BAŞLAT": self.scene.addItem(BaslatDurdurBlogu(p.x(), p.y(), tip, "#34c759", tip))
        elif tip == "DURDUR": self.scene.addItem(BaslatDurdurBlogu(p.x(), p.y(), tip, "#ff3b30", tip))
        elif tip == "İŞLEM": self.scene.addItem(IslemDegiskenBlogu(p.x(), p.y(), tip, "#5e5ce6", tip))
        elif tip == "DEĞİŞKEN": self.scene.addItem(IslemDegiskenBlogu(p.x(), p.y(), tip, "#af52de", tip))
        elif tip == "EĞER": self.scene.addItem(KararBlogu(p.x(), p.y(), tip))
        elif tip in ["GİRİŞ", "ÇIKIŞ"]:
            renk = "#30d158" if tip == "GİRİŞ" else "#32ade6"
            self.scene.addItem(GirisCikisBlogu(p.x(), p.y(), tip, renk, tip))
        elif tip == "DÜĞÜM": self.scene.addItem(DugumBlogu(p.x(), p.y()))

    def baglanti_sec(self, item): self.secili_baslangic = item
    def baglanti_kur(self, hedef):
        bas = self.secili_baslangic
        if bas == hedef: self.secili_baslangic = None; return
        cikanlar = [c for c in bas.baglantilar if c.baslangic == bas]
        if isinstance(bas, KararBlogu):
            if len(cikanlar) >= 2: self.hata_log("EĞER'den 2 ok çıkabilir."); self.secili_baslangic = None; return
            etiket = "Evet" if len(cikanlar) == 0 else "Hayır"
        else:
            if len(cikanlar) >= 1: self.hata_log(f"{bas.tip_adi}'den 1 ok çıkabilir."); self.secili_baslangic = None; return
            etiket = ""
        c = Baglanticizgisi(bas, hedef, etiket)
        self.scene.addItem(c); bas.baglantilar.append(c); hedef.baglantilar.append(c)
        self.secili_baslangic = None

    def blok_sil(self, blok):
        if self.secili_baslangic == blok: self.secili_baslangic = None
        blok.sil(self.scene)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ModernFlowApp(); ex.show()
    sys.exit(app.exec_())