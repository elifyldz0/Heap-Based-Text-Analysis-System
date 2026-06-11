"""
Metin Dosyasındaki Kelime Sayısını Heap Yapısı ile Sıralayan Program

Program bir txt dosyasından okuduğu kelimeleri sayarak, bir Min-Heap yapısı
kullanarak sıralanmış şekilde sonuçları gösterir.

Sıralama Kriterleri (2 anahtar):
1. Kelimenin ilk harfi (A'dan Z'ye)
2. Aynı harfle başlayan kelimeler için: sayı (çok olandan az olana)
"""

import re
from dataclasses import dataclass


# Türkçe alfabesi (başında 'ç' ve 'ğ' gibi karakterler)
TURKISH_ALPHABET = "abcçdefgğhıijklmnoöprsştuüvyz"
LETTER_ORDER = {letter: index for index, letter in enumerate(TURKISH_ALPHABET)}

# Türkçe karakterlerin normalize edilmesi
TR_LOWER_MAP = str.maketrans({"I": "ı", "İ": "i"})

# Kelime çıkartma regex'i - Türkçe karakterleri destekler
WORD_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]+")


@dataclass
class WordEntry:
    """Heap'te saklanacak veri: kelime ve sayı"""
    word: str
    count: int


class WordHeap:
    """
    Kelime frekansını sıralayan Min-Heap yapısı.
    
    Özellikler:
    - İlk harfe göre artan sırayla (A'dan Z'ye)
    - Aynı harfta: frekansa göre azalan sırayla (çok olanlar önce)
    - Kelime güncellemesi için O(log n) zaman karmaşıklığı
    """

    def __init__(self):
        self.heap = []  # Heap veri yapısı (dizi olarak temsil)
        self.positions = {}  # Hızlı erişim için: kelime -> index

    def _letter_rank(self, word):
        """
        Kelimenin ilk harfinin Türkçe alfabedeki sırası.
        Örn: 'ankara' -> 0 (a), 'kocaeli' -> 13 (k)
        """
        first_letter = word[0]
        return LETTER_ORDER.get(first_letter, len(LETTER_ORDER) + ord(first_letter))

    def _priority(self, entry):
        """
        Heap'te kullanılan öncelik kriteri (2 anahtar):
        1. İlk harfin sırası (artan)
        2. Frekans (negatif yapılarak azalan)
        
        Örn: ('ankara', 2) -> (0, -2)
             ('kocaeli', 1) -> (13, -1)
        """
        return (self._letter_rank(entry.word), -entry.count)

    def _comes_before(self, left, right):
        """Min-heap: daha düşük öncelikli eleman üste gelmeli"""
        return self._priority(left) < self._priority(right)

    def _swap(self, first_index, second_index):
        """İki düğümü heap'te değiştir ve pozisyon haritasını güncelle"""
        self.heap[first_index], self.heap[second_index] = self.heap[second_index], self.heap[first_index]
        self.positions[self.heap[first_index].word] = first_index
        self.positions[self.heap[second_index].word] = second_index

    def _sift_up(self, index):
        """
        Yeni/güncellenmiş düğümü yukarı doğru hareket ettir.
        Eğer parent'den daha düşük öncelikli ise, parent ile yer değiştir.
        """
        while index > 0:
            parent_index = (index - 1) // 2
            if not self._comes_before(self.heap[index], self.heap[parent_index]):
                break

            self._swap(index, parent_index)
            index = parent_index

    def _sift_down(self, index):
        """
        Root düğümü aşağı doğru hareket ettir.
        Çocuklarından daha yüksek öncelikli ise, en düşük öncelikli çocuk ile yer değiştir.
        """
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
        """
        Kelimeyi ekle veya sayısını güncelle.
        
        - Kelime zaten varsa: sayısı 1 arttır ve sift_up yap
        - Yeni kelime ise: sona ekle ve sift_up yap
        """
        if word in self.positions:
            index = self.positions[word]
            self.heap[index].count += 1
            self._sift_up(index)
            return

        self.heap.append(WordEntry(word, 1))
        new_index = len(self.heap) - 1
        self.positions[word] = new_index
        self._sift_up(new_index)

    def pop(self):
        """
        Heap'ten en yüksek öncelikli elemanı çıkar (root).
        Geriye kalan elemanları heap'e uygun hale getirmek için sift_down yap.
        """
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
        """Heap boş mu?"""
        return len(self.heap) == 0

    def sorted_entries(self):
        """
        Heap'teki tüm elemanları sıralanmış düzende döndür.
        Heap'i değiştirmemek için kopyasını oluştur ve pop işlemi yap.
        """
        copied_heap = WordHeap()
        copied_heap.heap = [WordEntry(entry.word, entry.count) for entry in self.heap]
        copied_heap.positions = {entry.word: index for index, entry in enumerate(copied_heap.heap)}

        entries = []
        while not copied_heap.is_empty():
            entries.append(copied_heap.pop())

        return entries


def normalize_word(word):
    """Kelimeyi normalize et: İ->i, I->ı ve tüm karakterleri küçük yap"""
    return word.translate(TR_LOWER_MAP).lower()


def count_words_with_heap(file_path):
    """
    Txt dosyasını oku ve kelimeleri heap'te sayarak sonuçları döndür.
    
    Args:
        file_path: Okunacak txt dosyasının yolu
    
    Returns:
        WordHeap nesnesi (kelimeleri sayı ile birlikte içeren)
    
    Raises:
        FileNotFoundError: Dosya bulunamadığı zaman
        UnicodeDecodeError: Dosya UTF-8 olarak okunamadığı zaman
    """
    word_heap = WordHeap()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Her satırdaki kelimeleri çıkart
            for raw_word in WORD_RE.findall(line):
                word_heap.add_or_update(normalize_word(raw_word))

    return word_heap


def print_result(word_heap):
    """Heap'teki kelimeleri sıralanmış düzende yazdır"""
    for entry in word_heap.sorted_entries():
        print(f"{entry.word}: {entry.count}")


def main():
    """
    Ana program:
    1. Kullanıcıdan dosya yolu iste
    2. Dosyayı oku ve kelimeleri say
    3. Sonuçları yazdır
    """
    file_path = input("Txt dosyasının yolunu giriniz: ").strip().strip('"').strip("'")

    try:
        word_heap = count_words_with_heap(file_path)
    except FileNotFoundError:
        print("Hata: Girilen dosya bulunamadı.")
        return
    except UnicodeDecodeError:
        print("Hata: Dosya UTF-8 formatında okunamadı.")
        return

    print_result(word_heap)


if __name__ == "__main__":
    main()
