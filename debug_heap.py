import re
import math
try:
    import tkinter as tk
except Exception:
    tk = None
import tempfile
import webbrowser
import os
from dataclasses import dataclass


TURKISH_ALPHABET = "abcçdefgğhıijklmnoöprsştuüvyz"
LETTER_ORDER = {letter: index for index, letter in enumerate(TURKISH_ALPHABET)}
TR_LOWER_MAP = str.maketrans({"I": "ı", "İ": "i"})
WORD_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]+")


@dataclass
class WordEntry:
    word: str
    count: int


class WordHeap:
    """İlk harfe göre artan, aynı ilk harfte sayıya göre azalan min-heap."""

    def __init__(self):
        self.heap = []
        self.positions = {}
        self.step = 0

    def _letter_rank(self, word):
        """Kelimenin ilk harfinin sıralaması (0-26 arasında)"""
        first_letter = word[0]
        return LETTER_ORDER.get(first_letter, len(LETTER_ORDER) + ord(first_letter))

    def _priority(self, entry):
        """
        Heap öncelik kriteri:
        1. İlk harf (küçükten büyüğe)
        2. Frekans (büyükten küçüğe) - negatif yaparak tersine çeviriyoruz
        """
        return (self._letter_rank(entry.word), -entry.count)

    def _comes_before(self, left, right):
        """Sol eleman sağ elemandan önce gelmeli mi? (Min-heap için)"""
        return self._priority(left) < self._priority(right)

    def _print_heap_state(self, action):
        """Heap durumunu görsel olarak yazdır"""
        self.step += 1
        print(f"\n{'='*50}")
        print(f"ADIM {self.step}: {action}")
        print(f"{'='*50}")
        if not self.heap:
            print("Heap boş")
        else:
            print("Heap durumu:")
            for i, entry in enumerate(self.heap):
                letter_rank = self._letter_rank(entry.word)
                priority = self._priority(entry)
                print(f"  [{i}] {entry.word} ({entry.count}) - letter_rank={letter_rank}, priority={priority}")
        print()

    def _swap(self, first_index, second_index):
        self.heap[first_index], self.heap[second_index] = self.heap[second_index], self.heap[first_index]
        self.positions[self.heap[first_index].word] = first_index
        self.positions[self.heap[second_index].word] = second_index

    def _sift_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            if not self._comes_before(self.heap[index], self.heap[parent_index]):
                break

            self._swap(index, parent_index)
            index = parent_index

    def _sift_down(self, index):
        size = len(self.heap)

        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            best_index = index

            if left_child < size and self._comes_before(self.heap[left_child], self.heap[best_index]):
                best_index = left_child

            if right_child < size and self._comes_before(self.heap[right_child], self.heap[best_index]):
                best_index = right_child

            if best_index == index:
                break

            self._swap(index, best_index)
            index = best_index

    def add_or_update(self, word):
        if word in self.positions:
            index = self.positions[word]
            old_count = self.heap[index].count
            self.heap[index].count += 1
            self._print_heap_state(f"'{word}' sayısı {old_count}'den {old_count+1}'e güncellendi")
            self._sift_up(index)
            self._print_heap_state(f"'{word}' sift_up sonrası")
            return

        self.heap.append(WordEntry(word, 1))
        new_index = len(self.heap) - 1
        self.positions[word] = new_index
        self._print_heap_state(f"'{word}' (1) eklendi")
        self._sift_up(new_index)
        self._print_heap_state(f"'{word}' sift_up sonrası")

    def pop(self):
        if not self.heap:
            raise IndexError("Boş heap'ten eleman çıkarılamaz.")

        root = self.heap[0]
        last = self.heap.pop()
        del self.positions[root.word]

        if self.heap:
            self.heap[0] = last
            self.positions[last.word] = 0
            self._sift_down(0)

        return root

    def is_empty(self):
        return len(self.heap) == 0

    def sorted_entries(self):
        copied_heap = WordHeap()
        copied_heap.heap = [WordEntry(entry.word, entry.count) for entry in self.heap]
        copied_heap.positions = {entry.word: index for index, entry in enumerate(copied_heap.heap)}

        entries = []
        while not copied_heap.is_empty():
            entries.append(copied_heap.pop())

        return entries


def normalize_word(word):
    return word.translate(TR_LOWER_MAP).lower()


def count_words_with_heap(file_path):
    word_heap = WordHeap()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            for raw_word in WORD_RE.findall(line):
                word_heap.add_or_update(normalize_word(raw_word))

    return word_heap


def print_result(word_heap):
    print("\n" + "="*50)
    print("FINAL SORTED RESULT")
    print("="*50)
    for entry in word_heap.sorted_entries():
        print(f"{entry.word}: {entry.count}")


def print_heap_tree(word_heap):
    """ASCII görselleştirme: heap içeriğini ikili ağaç şeklinde yazdırır.

    Her düğüm array indeksine göre gösterilir: [i] kelime (count)
    """
    heap = word_heap.heap

    def label(i):
        e = heap[i]
        return f"[{i}] {e.word} ({e.count})"

    def _print_subtree(i, prefix="", is_left=None):
        if i >= len(heap):
            return

        # connector çizgisi (root için boş)
        if is_left is True:
            connector = "├── "
        elif is_left is False:
            connector = "└── "
        else:
            connector = ""

        if connector:
            print(prefix + connector + label(i))
        else:
            # root
            print(label(i))

        left = 2 * i + 1
        right = 2 * i + 2

        # Sol çocuk
        if left < len(heap):
            # Eğer sağ çocuk varsa, sol çocuğun üstünde devam eden bir dikey çizgi olmalı
            new_prefix = prefix + ("│   " if right < len(heap) else "    ")
            _print_subtree(left, new_prefix, True)

        # Sağ çocuk
        if right < len(heap):
            new_prefix = prefix + "    "
            _print_subtree(right, new_prefix, False)


    # start from root
    _print_subtree(0)


def show_heap_window(word_heap):
    """Ayrı bir pencere açıp heap'i grafikte gösterir (tkinter kullanır)."""
    if tk is None:
        raise RuntimeError("tkinter yok")

    heap = word_heap.heap
    if not heap:
        # küçük uyarı penceresi
        root = tk.Tk()
        root.title("Heap Görselleştirici")
        tk.Label(root, text="Heap boş").pack(padx=20, pady=20)
        root.mainloop()
        return

    # pencere + canvas boyutu
    width = 800
    height = 400
    padding_x = 40
    level_height = 80

    root = tk.Tk()
    root.title("Heap Görselleştirme")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    # Düğüm pozisyonlarını hesapla: her seviye için eşit aralık
    positions = {}
    max_index = len(heap) - 1
    max_level = int(math.floor(math.log2(max_index))) if max_index > 0 else 0

    for i in range(len(heap)):
        level = int(math.floor(math.log2(i+1))) if i > 0 else 0
        level_start = 2**level - 1
        index_in_level = i - level_start
        nodes_in_level = 2**level
        avail_width = width - 2 * padding_x
        x = padding_x + (index_in_level + 0.5) * (avail_width / nodes_in_level)
        y = 20 + level * level_height
        positions[i] = (x, y)

    # çizgiler
    for i in range(len(heap)):
        left = 2 * i + 1
        right = 2 * i + 2
        x1, y1 = positions[i]
        if left < len(heap):
            x2, y2 = positions[left]
            canvas.create_line(x1, y1+30, x2, y2-30, width=3, fill="#2c3e50")
        if right < len(heap):
            x2, y2 = positions[right]
            canvas.create_line(x1, y1+30, x2, y2-30, width=3, fill="#2c3e50")

    # düğümler
    r = 30
    for i, entry in enumerate(heap):
        x, y = positions[i]
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="#e8f4f8", outline="#2c3e50", width=2)
        canvas.create_text(x, y-5, text=entry.word, font=("Helvetica", 11, "bold"), fill="#000")
        canvas.create_text(x, y+10, text=str(entry.count), font=("Helvetica", 10, "bold"), fill="#e74c3c")

    # pencereyi çalıştır
    root.mainloop()


def show_heap_in_browser(word_heap):
    """HTML+SVG olarak heap'i oluşturur ve varsayılan tarayıcıda açar."""
    heap = word_heap.heap
    if not heap:
        html = '<html><body><h3>Heap boş</h3></body></html>'
    else:
        # basit SVG oluştur
        width = 1000
        level_height = 100
        padding_x = 40

        # hesapla max level
        max_index = len(heap) - 1
        max_level = int(math.floor(math.log2(max_index))) if max_index > 0 else 0
        height = (max_level + 1) * level_height + 60

        nodes = []
        for i in range(len(heap)):
            level = int(math.floor(math.log2(i+1))) if i > 0 else 0
            level_start = 2**level - 1
            index_in_level = i - level_start
            nodes_in_level = 2**level
            avail_width = width - 2 * padding_x
            x = padding_x + (index_in_level + 0.5) * (avail_width / nodes_in_level)
            y = 30 + level * level_height
            nodes.append((i, x, y, heap[i].word, heap[i].count))

        svg_parts = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']

        # çizgiler
        for i, x, y, w, c in nodes:
            left = 2 * i + 1
            right = 2 * i + 2
            if left < len(heap):
                x2 = nodes[left][1]
                y2 = nodes[left][2]
                svg_parts.append(f'<line x1="{x}" y1="{y+28}" x2="{x2}" y2="{y2-28}" stroke="#2c3e50" stroke-width="3" />')
            if right < len(heap):
                x2 = nodes[right][1]
                y2 = nodes[right][2]
                svg_parts.append(f'<line x1="{x}" y1="{y+28}" x2="{x2}" y2="{y2-28}" stroke="#2c3e50" stroke-width="3" />')

        # düğümler
        for i, x, y, w, c in nodes:
            svg_parts.append(f'<g>')
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="28" fill="#e8f4f8" stroke="#2c3e50" stroke-width="2" />')
            svg_parts.append(f'<text x="{x}" y="{y-6}" text-anchor="middle" font-size="13" font-family="Helvetica" font-weight="bold" fill="#000">{w}</text>')
            svg_parts.append(f'<text x="{x}" y="{y+12}" text-anchor="middle" font-size="12" font-family="Helvetica" font-weight="bold" fill="#e74c3c">{c}</text>')
            svg_parts.append(f'</g>')

        svg_parts.append('</svg>')
        svg = '\n'.join(svg_parts)
        html = f'<!doctype html><html><head><meta charset="utf-8"><title>Heap Görselleştirme</title></head><body>{svg}</body></html>'

    # write to temp file and open
    fd, path = tempfile.mkstemp(suffix='.html', prefix='heap_vis_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(html)

    webbrowser.open('file://' + path)


def main():
    file_path = input("Txt dosyasının yolunu giriniz: ").strip().strip('"').strip("'")

    try:
        word_heap = count_words_with_heap(file_path)
    except FileNotFoundError:
        print("Hata: Girilen dosya bulunamadı.")
        return
    except UnicodeDecodeError:
        print("Hata: Dosya UTF-8 formatında okunamadı.")
        return

    # Heap yapısının son halini ayrı pencerede görselleştir (varsa tkinter kullan)
    if tk is not None:
        try:
            show_heap_window(word_heap)
        except Exception as e:
            # GUI açılmazsa terminalde ASCII ağaç yazdır
            print("(GUI açılamadı, terminale fallback yapılıyor)")
            print("\n" + "="*50)
            print("HEAP TREE (final heap içeriği)")
            print("="*50)
            if word_heap.is_empty():
                print("Heap boş")
            else:
                print_heap_tree(word_heap)
    else:
        # tkinter yoksa önce tarayıcıda göster (HTML+SVG); tarayıcı açılamazsa terminale yazdır
        try:
            show_heap_in_browser(word_heap)
        except Exception:
            print("(tarayıcı açılamadı — terminale yazdırılıyor)")
            print("\n" + "="*50)
            print("HEAP TREE (final heap içeriği)")
            print("="*50)
            if word_heap.is_empty():
                print("Heap boş")
            else:
                print_heap_tree(word_heap)

    print_result(word_heap)


if __name__ == "__main__":
    main()
