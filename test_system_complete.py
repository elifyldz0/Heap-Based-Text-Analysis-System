"""
TEST VE DOĞRULAMA SİSTEMİ
====================================

Bu modül heap veri yapısının tüm bileşenlerini test eder:
1. Kelime normalleştirme
2. Heap ekleme (add_or_update)
3. Heap sift-up işlemi
4. Heap sift-down işlemi
5. Kelime sıralama
6. Dosya okuma ve işleme
7. Min-heap özelliğinin korunması
8. Edge case'ler (boş heap, tekrar edenler vb.)
"""

import unittest
from pathlib import Path
import tempfile
import os
from kelime_heap import (
    WordEntry, WordHeap, normalize_word, count_words_with_heap,
    LETTER_ORDER, TURKISH_ALPHABET, WORD_RE
)


class TestNormalization(unittest.TestCase):
    """Kelime normalleştirme testleri"""

    def test_lowercase_conversion(self):
        """Büyük harfleri küçüğe dönüştürme"""
        self.assertEqual(normalize_word("ELMA"), "elma")
        self.assertEqual(normalize_word("Armut"), "armut")

    def test_turkish_i_normalization(self):
        """Türkçe I/İ karakterleri normalleştirme"""
        self.assertEqual(normalize_word("İstanbul"), "istanbul")
        self.assertEqual(normalize_word("KIZI"), "kızı")

    def test_turkish_special_chars(self):
        """Türkçe özel karakterler korunma"""
        self.assertEqual(normalize_word("çiçek"), "çiçek")
        self.assertEqual(normalize_word("ğuğu"), "ğuğu")
        self.assertEqual(normalize_word("Şişe"), "şişe")
        self.assertEqual(normalize_word("ÖRDEK"), "ördek")
        self.assertEqual(normalize_word("Üzüm"), "üzüm")

    def test_mixed_case_special_chars(self):
        """Karışık harf ve Türkçe karakterler"""
        self.assertEqual(normalize_word("ÇİÇEK"), "çiçek")
        self.assertEqual(normalize_word("İZMİR"), "izmir")


class TestWordHeapBasic(unittest.TestCase):
    """Heap temel işlemleri testleri"""

    def setUp(self):
        """Her test öncesi yeni heap oluştur"""
        self.heap = WordHeap()

    def test_heap_initialization(self):
        """Heap'in başlangıçta boş olması"""
        self.assertTrue(self.heap.is_empty())
        self.assertEqual(len(self.heap.heap), 0)
        self.assertEqual(len(self.heap.positions), 0)

    def test_single_word_insertion(self):
        """Tek kelime ekleme"""
        self.heap.add_or_update("elma")
        self.assertFalse(self.heap.is_empty())
        self.assertEqual(len(self.heap.heap), 1)
        self.assertEqual(self.heap.heap[0].word, "elma")
        self.assertEqual(self.heap.heap[0].count, 1)

    def test_word_count_increment(self):
        """Aynı kelimeyi birden fazla ekleme"""
        self.heap.add_or_update("elma")
        self.heap.add_or_update("elma")
        self.heap.add_or_update("elma")
        self.assertEqual(len(self.heap.heap), 1)
        self.assertEqual(self.heap.heap[0].count, 3)

    def test_multiple_words_insertion(self):
        """Farklı kelimeleri ekleme"""
        self.heap.add_or_update("elma")
        self.heap.add_or_update("armut")
        self.heap.add_or_update("çiçek")
        self.assertEqual(len(self.heap.heap), 3)

    def test_positions_tracking(self):
        """Kelime pozisyonlarının doğru takip edilmesi"""
        self.heap.add_or_update("elma")
        self.heap.add_or_update("armut")
        self.heap.add_or_update("çiçek")
        
        self.assertIn("elma", self.heap.positions)
        self.assertIn("armut", self.heap.positions)
        self.assertIn("çiçek", self.heap.positions)
        
        # Pozisyon indeksleri tutarlı olmalı
        for word, pos in self.heap.positions.items():
            self.assertEqual(self.heap.heap[pos].word, word)


class TestHeapOrdering(unittest.TestCase):
    """Heap sıralama mantığı testleri"""

    def setUp(self):
        self.heap = WordHeap()

    def test_letter_rank_ordering(self):
        """Harflerin sırasının doğru hesaplanması"""
        self.assertEqual(self.heap._letter_rank("armut"), LETTER_ORDER["a"])
        self.assertEqual(self.heap._letter_rank("çiçek"), LETTER_ORDER["ç"])
        self.assertEqual(self.heap._letter_rank("elma"), LETTER_ORDER["e"])
        self.assertTrue(self.heap._letter_rank("armut") < self.heap._letter_rank("elma"))
        self.assertTrue(self.heap._letter_rank("çiçek") < self.heap._letter_rank("elma"))

    def test_priority_calculation(self):
        """Öncelik puanının doğru hesaplanması"""
        entry1 = WordEntry("armut", 3)
        entry2 = WordEntry("elma", 2)
        
        priority1 = self.heap._priority(entry1)
        priority2 = self.heap._priority(entry2)
        
        # (harf_sırası, -sayı)
        self.assertLess(priority1, priority2)  # armut > elma (a < e)

    def test_same_letter_different_count(self):
        """Aynı harfle başlayan kelimeler sayıya göre sıralanmalı"""
        # b harfiyle başlayan iki kelime
        bisiklet = WordEntry("bisiklet", 1)
        balık = WordEntry("balık", 2)
        
        priority_bisiklet = self.heap._priority(bisiklet)
        priority_balık = self.heap._priority(balık)
        
        # balık daha çok sayıya sahip (2 > 1), öncelikli olmalı
        self.assertLess(priority_balık, priority_bisiklet)

    def test_min_heap_property_after_insertion(self):
        """Heap özelliğinin korunması - parent child'den öncelikli"""
        words = ["elma", "armut", "çiçek", "balık", "bisiklet"]
        for word in words:
            self.heap.add_or_update(word)
        
        # Parent her zaman child'den öncelikli olmalı
        for i in range(len(self.heap.heap)):
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < len(self.heap.heap):
                parent_priority = self.heap._priority(self.heap.heap[i])
                left_priority = self.heap._priority(self.heap.heap[left])
                self.assertLessEqual(parent_priority, left_priority)
            
            if right < len(self.heap.heap):
                parent_priority = self.heap._priority(self.heap.heap[i])
                right_priority = self.heap._priority(self.heap.heap[right])
                self.assertLessEqual(parent_priority, right_priority)

    def test_min_heap_property_after_update(self):
        """Sayı güncellemesinden sonra heap özelliğinin korunması"""
        self.heap.add_or_update("armut")
        self.heap.add_or_update("elma")
        self.heap.add_or_update("çiçek")
        
        # armut'u 5 kez ekle (sayısını arttır)
        for _ in range(5):
            self.heap.add_or_update("armut")
        
        # Min-heap özelliğinin hala korunmuş olmalı
        for i in range(len(self.heap.heap)):
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < len(self.heap.heap):
                parent_priority = self.heap._priority(self.heap.heap[i])
                left_priority = self.heap._priority(self.heap.heap[left])
                self.assertLessEqual(parent_priority, left_priority)
            
            if right < len(self.heap.heap):
                parent_priority = self.heap._priority(self.heap.heap[i])
                right_priority = self.heap._priority(self.heap.heap[right])
                self.assertLessEqual(parent_priority, right_priority)


class TestHeapOperations(unittest.TestCase):
    """Pop ve sorted_entries operasyonları testleri"""

    def setUp(self):
        self.heap = WordHeap()

    def test_pop_from_empty_heap(self):
        """Boş heap'ten pop yapmak hata vermeli"""
        with self.assertRaises(IndexError):
            self.heap.pop()

    def test_pop_single_element(self):
        """Tek elemanı çıkarma"""
        self.heap.add_or_update("elma")
        entry = self.heap.pop()
        
        self.assertEqual(entry.word, "elma")
        self.assertEqual(entry.count, 1)
        self.assertTrue(self.heap.is_empty())

    def test_pop_maintains_heap_property(self):
        """Pop işlemi heap özelliğini korumalı"""
        words = ["elma", "armut", "çiçek", "balık", "bisiklet"]
        for word in words:
            self.heap.add_or_update(word)
        
        first = self.heap.pop()
        
        # Pop sonrası heap özelliği korunmalı
        for i in range(len(self.heap.heap)):
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < len(self.heap.heap):
                parent_priority = self.heap._priority(self.heap.heap[i])
                left_priority = self.heap._priority(self.heap.heap[left])
                self.assertLessEqual(parent_priority, left_priority)

    def test_sorted_entries_order(self):
        """sorted_entries'in doğru sırada elemanlar döndürmesi"""
        words_with_counts = [
            ("armut", 3), ("balık", 2), ("bisiklet", 1),
            ("çanta", 2), ("çiçek", 1), ("elma", 2)
        ]
        
        for word, count in words_with_counts:
            for _ in range(count):
                self.heap.add_or_update(word)
        
        sorted_result = self.heap.sorted_entries()
        
        # Sıralanmış sonuç
        expected_order = ["armut", "balık", "bisiklet", "çanta", "çiçek", "elma"]
        actual_order = [entry.word for entry in sorted_result]
        
        self.assertEqual(actual_order, expected_order)

    def test_sorted_entries_doesnt_modify_heap(self):
        """sorted_entries heap'i değiştirmemeli"""
        self.heap.add_or_update("elma")
        self.heap.add_or_update("armut")
        
        original_size = len(self.heap.heap)
        _ = self.heap.sorted_entries()
        
        self.assertEqual(len(self.heap.heap), original_size)
        self.assertEqual(len(self.heap.positions), original_size)


class TestFileProcessing(unittest.TestCase):
    """Dosya okuma ve işleme testleri"""

    def setUp(self):
        """Geçici dosyalar için temp dizini kullan"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Geçici dosyaları sil"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_file_not_found(self):
        """Olmayan dosya için hata"""
        with self.assertRaises(FileNotFoundError):
            count_words_with_heap(os.path.join(self.temp_dir, "nonexistent.txt"))

    def test_empty_file(self):
        """Boş dosya işleme"""
        file_path = os.path.join(self.temp_dir, "empty.txt")
        Path(file_path).write_text("", encoding="utf-8")
        
        heap = count_words_with_heap(file_path)
        self.assertTrue(heap.is_empty())

    def test_single_line_single_word(self):
        """Tek satır tek kelime"""
        file_path = os.path.join(self.temp_dir, "single.txt")
        Path(file_path).write_text("elma", encoding="utf-8")
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 1)
        self.assertEqual(heap.heap[0].word, "elma")
        self.assertEqual(heap.heap[0].count, 1)

    def test_multiple_words_same_line(self):
        """Aynı satırda birden fazla kelime"""
        file_path = os.path.join(self.temp_dir, "multi.txt")
        Path(file_path).write_text("elma armut çiçek", encoding="utf-8")
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 3)

    def test_word_count_across_lines(self):
        """Satırlar arasında kelime sayımı"""
        file_path = os.path.join(self.temp_dir, "lines.txt")
        Path(file_path).write_text(
            "elma armut\n"
            "elma çiçek\n"
            "armut armut",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        sorted_entries = heap.sorted_entries()
        result = {entry.word: entry.count for entry in sorted_entries}
        
        self.assertEqual(result["elma"], 2)
        self.assertEqual(result["armut"], 3)
        self.assertEqual(result["çiçek"], 1)

    def test_case_insensitive_counting(self):
        """Büyük/küçük harf farklılığına rağmen aynı sayım"""
        file_path = os.path.join(self.temp_dir, "case.txt")
        Path(file_path).write_text(
            "ELMA elma Elma",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 1)
        self.assertEqual(heap.heap[0].count, 3)

    def test_special_characters_extraction(self):
        """Türkçe özel karakterleri içeren kelimeler"""
        file_path = os.path.join(self.temp_dir, "turkish.txt")
        Path(file_path).write_text(
            "çiçek ğuğu şişe ördek üzüm",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 5)
        words = {entry.word for entry in heap.heap}
        
        self.assertIn("çiçek", words)
        self.assertIn("ğuğu", words)
        self.assertIn("şişe", words)
        self.assertIn("ördek", words)
        self.assertIn("üzüm", words)

    def test_punctuation_removal(self):
        """Noktalama işaretleri kelimelere dahil edilmemeli"""
        file_path = os.path.join(self.temp_dir, "punct.txt")
        Path(file_path).write_text(
            "elma, armut! çiçek?",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        words = {entry.word for entry in heap.heap}
        
        # Noktalama işaretleri ayrı birer sözcük değildir
        self.assertIn("elma", words)
        self.assertIn("armut", words)
        self.assertIn("çiçek", words)
        self.assertNotIn(",", words)
        self.assertNotIn("!", words)
        self.assertNotIn("?", words)


class TestIntegration(unittest.TestCase):
    """Bütünleşik (Integration) testleri"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_complete_workflow(self):
        """Tam iş akışı: dosya oku → heap oluştur → sırala"""
        file_path = os.path.join(self.temp_dir, "workflow.txt")
        Path(file_path).write_text(
            "Elma elma armut armut armut\n"
            "Balık bisiklet balık\n"
            "Çanta çanta çiçek\n",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        sorted_result = heap.sorted_entries()
        
        expected = [
            ("armut", 3), ("balık", 2), ("bisiklet", 1),
            ("çanta", 2), ("çiçek", 1), ("elma", 2)
        ]
        actual = [(entry.word, entry.count) for entry in sorted_result]
        
        self.assertEqual(actual, expected)

    def test_large_file_processing(self):
        """Büyük dosya işleme"""
        file_path = os.path.join(self.temp_dir, "large.txt")
        
        # 1000 satır, her satırda tekrar eden kelimeler
        content = "\n".join(["elma armut çiçek"] * 100)
        Path(file_path).write_text(content, encoding="utf-8")
        
        heap = count_words_with_heap(file_path)
        sorted_result = heap.sorted_entries()
        result = {entry.word: entry.count for entry in sorted_result}
        
        self.assertEqual(result["armut"], 100)
        self.assertEqual(result["çiçek"], 100)
        self.assertEqual(result["elma"], 100)

    def test_duplicate_words_with_different_cases(self):
        """Farklı büyük/küçük harf kombinasyonları"""
        file_path = os.path.join(self.temp_dir, "cases.txt")
        Path(file_path).write_text(
            "ELMA Elma elma ELmA eLmA",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 1)
        self.assertEqual(heap.heap[0].count, 5)


class TestEdgeCases(unittest.TestCase):
    """Edge case'ler ve özel durumlar"""

    def setUp(self):
        self.heap = WordHeap()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_single_character_words(self):
        """Tek karakterli sözcükler"""
        self.heap.add_or_update("a")
        self.heap.add_or_update("ç")
        
        self.assertEqual(len(self.heap.heap), 2)

    def test_very_long_word(self):
        """Çok uzun sözcük"""
        long_word = "a" * 1000
        self.heap.add_or_update(long_word)
        
        self.assertEqual(self.heap.heap[0].word, long_word)
        self.assertEqual(self.heap.heap[0].count, 1)

    def test_many_duplicates(self):
        """Çok sayıda tekrar"""
        for _ in range(1000):
            self.heap.add_or_update("elma")
        
        self.assertEqual(len(self.heap.heap), 1)
        self.assertEqual(self.heap.heap[0].count, 1000)

    def test_file_with_empty_lines(self):
        """Boş satırları içeren dosya"""
        file_path = os.path.join(self.temp_dir, "empty_lines.txt")
        Path(file_path).write_text(
            "elma\n\n\narmut\n",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 2)

    def test_file_with_whitespace_only_lines(self):
        """Sadece boşluk içeren satırlar"""
        file_path = os.path.join(self.temp_dir, "whitespace.txt")
        Path(file_path).write_text(
            "elma\n   \n\t\narmut",
            encoding="utf-8"
        )
        
        heap = count_words_with_heap(file_path)
        self.assertEqual(len(heap.heap), 2)


def run_all_tests():
    """Tüm testleri çalıştır ve rapor oluştur"""
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Tüm test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestWordHeapBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestHeapOrdering))
    suite.addTests(loader.loadTestsFromTestCase(TestHeapOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestFileProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Testleri çalıştır (verbosity=0 = sessiz mod)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_all_tests()
    
    # Kısa özet rapor
    print("\n" + "=" * 50)
    print("TEST SONUÇLARI")
    print("=" * 50)
    print(f"Toplam Test: {result.testsRun}")
    print(f"✓ Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ Başarısız: {len(result.failures)}")
    print(f"⚠ Hatalar: {len(result.errors)}")
    print("=" * 50)
