import statistics
import os
import sys
from PyQt5.QtCore import Qt
import re
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from scraper import get_iphone_coustoms_posts
from PyQt5.QtWidgets import QTableWidgetItem
import webbrowser
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QCursor


def resource_path(relative_path):
    """برگرداندن مسیر فایل‌ها در حالت عادی و فایل exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("UI/divar_UI/mainwindow.ui"), self)  # مسیر فایل ui
        self.tablePosts.setSelectionBehavior(self.tablePosts.SelectRows)
        self.tablePosts.setEditTriggers(self.tablePosts.NoEditTriggers)
        self.tablePosts.setAlternatingRowColors(True)
        self.tablePosts.verticalHeader().setVisible(False)
        self.setWindowIcon(QIcon(resource_path("Ikoon/ikom2.ico")))
        self.setWindowTitle("DivarPro V1.1.0")
        self.pushButton_2.clicked.connect(self.get_posts)
        self.tablePosts.doubleClicked.connect(self.open_post)

        self.tablePosts.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablePosts.customContextMenuRequested.connect(self.show_menu)

    def open_post(self):
        row = self.tablePosts.currentRow()

        link = self.posts[row]["link"]

        webbrowser.open(link)

    def show_menu(self, position):

        menu = QMenu()

        openAction = menu.addAction("🌐 Open in Browser")
        copyLink = menu.addAction("📋 Copy Link")
        copyToken = menu.addAction("🪪 Copy Token")

        action = menu.exec_(QCursor.pos())

        row = self.tablePosts.currentRow()

        if row == -1:
            return

        if action == openAction:
            webbrowser.open(self.posts[row]["link"])

        elif action == copyLink:
            QApplication.clipboard().setText(self.posts[row]["link"])

        elif action == copyToken:
            QApplication.clipboard().setText(self.posts[row]["token"])

    def convert_price(self, price_text):
        numbers = re.sub(r"[^\d]", "", price_text)

        if numbers == "":
            return None

        return int(numbers)

    def get_posts(self):
        city = self.comboBox_city.currentText()
        brand = self.comboBox_Brand.currentText()
        model = self.comboBox_Model.currentText()

        print(city)
        print(brand)
        print(model)

        self.posts = get_iphone_coustoms_posts(model)

        # پاک کردن اطلاعات قبلی
        self.tablePosts.clearContents()

        # تعداد ردیف‌ها
        self.tablePosts.setRowCount(len(self.posts))

        # پر کردن جدول
        for row, post in enumerate(self.posts):
            self.tablePosts.setItem(
                row,
                0,
                QTableWidgetItem(post["title"])
            )

            self.tablePosts.setItem(
                row,
                1,
                QTableWidgetItem(post["price"])
            )

            self.tablePosts.setItem(
                row,
                2,
                QTableWidgetItem(post["city"])
            )

            self.tablePosts.setItem(
                row,
                3,
                QTableWidgetItem(post["date"])
            )
        prices = []

        for post in self.posts:
            price = self.convert_price(post["price"])

            if price is not None:
                prices.append(price)

        # اگر هیچ قیمت معتبری وجود نداشت
        if not prices:
            self.labelMin.setText("----")
            self.labelMax.setText("----")
            self.labelAverage.setText("----")
            return

        # محاسبه میانه قیمت‌ها
        median = statistics.median(prices)

        # محدوده قابل قبول (60٪ تا 140٪ میانه)
        min_limit = median * 0.6
        max_limit = median * 1.4

        # حذف قیمت‌های غیرمنطقی
        filtered_prices = []

        for price in prices:
            if min_limit <= price <= max_limit:
                filtered_prices.append(price)

        # اگر بعد از فیلتر چیزی باقی نماند
        if not filtered_prices:
            self.labelMin.setText("----")
            self.labelMax.setText("----")
            self.labelAverage.setText("----")
            return

        # محاسبه آمار
        minimum = min(filtered_prices)
        maximum = max(filtered_prices)
        average = sum(filtered_prices) // len(filtered_prices)

        # نمایش در UI
        self.labelMin.setText(f"{minimum:,} تومان")
        self.labelMax.setText(f"{maximum:,} تومان")
        self.labelAverage.setText(f"{average:,} تومان")

        # اطلاعات برای دیباگ
        print(f"تعداد کل آگهی‌ها: {len(prices)}")
        print(f"تعداد بعد از فیلتر: {len(filtered_prices)}")
        print(f"حذف شده: {len(prices) - len(filtered_prices)}")

        print(f"کمترین: {minimum:,}")
        print(f"بیشترین: {maximum:,}")
        print(f"میانگین: {average:,}")

        print(prices)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
