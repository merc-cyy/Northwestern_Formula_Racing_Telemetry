import unittest
from analysis.common.parsers.telem.telem import (
    TelemTokenReader,
    TelemTokenizer,
    TelemBuilder,
    TelemTelemetryConfig,
    TelemTokenType
)


class TestTelemTokenReader(unittest.TestCase):
    def test_empty(self):
        reader = TelemTokenReader("")
        self.assertIsNone(reader.peekNextWord())
        self.assertFalse(reader.moveWord())

    def test_single_word(self):
        reader = TelemTokenReader("hello")
        w = reader.peekNextWord()
        self.assertEqual(w, "hello")
        w2 = reader.peekNextWord()
        self.assertEqual(w2, "hello")
        self.assertTrue(reader.moveWord())
        self.assertIsNone(reader.peekNextWord())

    def test_multiple_words(self):
        reader = TelemTokenReader(" one\t two\nthree   four ")
        self.assertEqual(reader.peekNextWord(), "one")
        reader.moveWord()
        self.assertEqual(reader.peekNextWord(), "two")
        reader.moveWord(2)
        self.assertEqual(reader.peekNextWord(), "four")
        reader.moveWord()
        self.assertIsNone(reader.peekNextWord())


class TestTelemTokenizer(unittest.TestCase):
    def tokenize(self, text):
        reader = TelemTokenReader(text)
        tok = TelemTokenizer(reader)
        tok.start()
        tokens = []
        while True:
            t = tok.next()
            tokens.append(t)
            if t.type == TelemTokenType.TT_EOF:
                break
        return tokens

    def test_prefixes(self):
        tokens = self.tokenize("!! > >> >>> >>>>")
        names = [t.type.name for t in tokens[:-1]]
        self.assertEqual(
            names,
            [
                "TT_OPTION_PREFIX",
                "TT_BOARD_PREFIX",
                "TT_MESSAGE_PREFIX",
                "TT_SIGNAL_PREFIX",
                "TT_ENUM_PREFIX",
            ],
        )

    def test_hex_and_int(self):
        tokens = self.tokenize("0x1A 42")
        self.assertEqual(tokens[0].type.name, "TT_HEX_INT")
        self.assertEqual(tokens[0].data, 0x1A)
        self.assertEqual(tokens[1].type.name, "TT_INT")
        self.assertEqual(tokens[1].data, 42)

    def test_float_and_negative(self):
        tokens = self.tokenize("-3.5 1e3 2E-2")
        self.assertEqual(tokens[0].type.name, "TT_FLOAT")
        self.assertAlmostEqual(tokens[0].data, -3.5)
        self.assertAlmostEqual(tokens[1].data, 1000.0)
        self.assertAlmostEqual(tokens[2].data, 0.02)

    def test_identifier(self):
        tokens = self.tokenize("Signal123 _under_score")
        self.assertEqual(tokens[0].type.name, "TT_IDENTIFIER")
        self.assertEqual(tokens[1].type.name, "TT_IDENTIFIER")


class TestTelemBuilder(unittest.TestCase):
    def build_config(self, cfg):
        reader = TelemTokenReader(cfg)
        tokenizer = TelemTokenizer(reader)
        builder = TelemBuilder(tokenizer)
        return builder.build()

    def test_simple(self):
        cfg = "!! logPeriodMs 100\n" "> B\n" ">> M 0x100 1\n" ">>> S1 uint8 0 8 1 0\n"
        config = self.build_config(cfg)
        self.assertEqual(config.options.get("logPeriodMs"), 100)
        self.assertEqual(len(config.boards), 1)
        board = config.boards[0]
        self.assertEqual(board.name, "B")
        self.assertEqual(len(board.messages), 1)

    def test_option_override(self):
        cfg = (
            "!! logPeriodMs 10\n"
            "!! logPeriodMs 20\n"
            "> B\n"
            ">> M 0x200 1\n"
            ">>> S uint8 0 8 1 0\n"
        )
        config = self.build_config(cfg)
        self.assertEqual(config.options.get("logPeriodMs"), 20)

    def test_sign_endian_override(self):
        cfg = "> B2\n" ">> M2 0x2A0 3\n" ">>> S2 int16 8 16 0.5 -1 signed big\n"
        config = self.build_config(cfg)
        sig = config.boards[0].messages[0].signals[0]
        self.assertTrue(sig.is_signed)
        self.assertEqual(sig.endianness, "big")

    def test_multiple_boards_error(self):
        cfg = "> B1\n" "> B2\n" ">> M 0x100 1\n" ">>> S uint8 0 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_duplicate_message_id_error(self):
        cfg = (
            "> B\n"
            ">> M1 0x100 1\n"
            ">>> S1 uint8 0 8 1 0\n"
            ">> M2 0x100 2\n"
            ">>> S2 uint16 0 16 1 0\n"
        )
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_signal_overlap_error(self):
        cfg = "> B\n" ">> M 0x100 2\n" ">>> S1 uint8 0 8 1 0\n" ">>> S2 uint8 4 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_signal_out_of_range_error(self):
        cfg = "> B\n" ">> M 0x100 1\n" ">>> S uint8 0 9 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_message_without_board_error(self):
        cfg = ">> M 0x100 1\n" ">>> S uint8 0 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_signal_without_message_error(self):
        cfg = "> B\n" ">>> S uint8 0 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_duplicate_signal_names_error(self):
        cfg = "> B\n" ">> M 0x100 2\n" ">>> S1 uint8 0 8 1 0\n" ">>> S1 uint8 8 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

    def test_duplicate_board_names_error(self):
        cfg = "> B\n" "> B\n" ">> M 0x100 1\n" ">>> S uint8 0 8 1 0\n"
        with self.assertRaises(ValueError):
            self.build_config(cfg)

