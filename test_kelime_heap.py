from pathlib import Path

from kelime_heap import count_words_with_heap


def run_test():
    test_file = Path("test_metin.txt")
    test_file.write_text(
        "Elma elma armut armut armut\n"
        "Balık bisiklet balık\n"
        "Çanta çanta çiçek\n",
        encoding="utf-8",
    )

    word_heap = count_words_with_heap(str(test_file))
    result = [(entry.word, entry.count) for entry in word_heap.sorted_entries()]
    expected = [
        ("armut", 3),
        ("balık", 2),
        ("bisiklet", 1),
        ("çanta", 2),
        ("çiçek", 1),
        ("elma", 2),
    ]

    if result == expected:
        print("Test başarılı.")
    else:
        print("Test başarısız.")
        print("Beklenen:", expected)
        print("Gelen:", result)


if __name__ == "__main__":
    run_test()
