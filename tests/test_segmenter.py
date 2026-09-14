import unittest
from src.transcript_cleaning.segmenter import create_timestamped_chunks

class SegmenterTests(unittest.TestCase):
    def test_empty_transcript(self):
        self.assertEqual(create_timestamped_chunks("demo.mp4", []), [])

    def test_distinct_ids_and_timestamps(self):
        segments = [
            {"start": 0.0, "end": 2.0, "text": "First sentence."},
            {"start": 2.0, "end": 4.0, "text": "Second sentence."},
        ]
        chunks = create_timestamped_chunks("demo_S1_Ep-01.mp4", segments,
                                          max_words=2, overlap_sentences=0)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len({c["video_id"] for c in chunks}), 2)
        self.assertEqual([(c["start"], c["end"]) for c in chunks], [(0.0, 2.0), (2.0, 4.0)])
        self.assertEqual([c["text"] for c in chunks], ["First sentence.", "Second sentence."])

if __name__ == "__main__":
    unittest.main()
