import unittest
from analysis.common.parsers.telem.telem import (
    TelemTokenReader,
    TelemTokenizer,
    TelemBuilder,
    TelemDataParser,
    TelemBitBuffer,
    TelemBitBufferHandle,
    TelemTelemetryConfig,
    TelemSignalDescription,
    TelemMessageDescription,
    TelemBoardDescription,
    TelemEnumEntry,
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
        # peek again without advancing
        w2 = reader.peekNextWord()
        self.assertEqual(w2, "hello")
        self.assertTrue(reader.moveWord())
        self.assertIsNone(reader.peekNextWord())

    def test_multiple_words(self):
        reader = TelemTokenReader(" one\t two\nthree   four ")
        # first word
        self.assertEqual(reader.peekNextWord(), "one")
        reader.moveWord()
        self.assertEqual(reader.peekNextWord(), "two")
        # skip two words at once
        reader.moveWord(2)
        self.assertEqual(reader.peekNextWord(), "four")
        reader.moveWord()
        self.assertIsNone(reader.peekNextWord())

class TestTelemTokenizer(unittest.TestCase):
    def setUp(self):
        pass

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

    def test_empty(self):
        tokens = self.tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TelemTokenType.TT_EOF)

    def test_prefixes(self):
        tokens = self.tokenize("!! > >> >>> >>>>")
        types = [t.type for t in tokens[:-1]]  # exclude EOF
        expected = [TelemTokenType.TT_OPTION_PREFIX,
                    TelemTokenType.TT_BOARD_PREFIX,
                    TelemTokenType.TT_MESSAGE_PREFIX,
                    TelemTokenType.TT_SIGNAL_PREFIX,
                    TelemTokenType.TT_ENUM_PREFIX]
        self.assertEqual(types, expected)

    def test_hex_and_int(self):
        tokens = self.tokenize("0x1A 42")
        self.assertEqual(tokens[0].type, TelemTokenType.TT_HEX_INT)
        self.assertEqual(tokens[0].data, 0x1A)
        self.assertEqual(tokens[1].type, TelemTokenType.TT_INT)
        self.assertEqual(tokens[1].data, 42)

    def test_float(self):
        tokens = self.tokenize("3.14")
        self.assertEqual(tokens[0].type, TelemTokenType.TT_FLOAT)
        self.assertAlmostEqual(tokens[0].data, 3.14, places=6)

    def test_identifier(self):
        tokens = self.tokenize("hello_world")
        self.assertEqual(tokens[0].type, TelemTokenType.TT_IDENTIFIER)
        self.assertEqual(tokens[0].data, "hello_world")

class TestTelemBuilder(unittest.TestCase):
    def test_simple_config(self):
        cfg = (
            "!! logPeriodMs 123\n"
            "> BOARD1\n"
            ">> MSG_A 0x100 2\n"
            ">>> SIG1 uint8 0 8 2 1\n"
        )
        reader = TelemTokenReader(cfg)
        tokenizer = TelemTokenizer(reader)
        builder = TelemBuilder(tokenizer)
        config = builder.build()
        # options
        self.assertIn("logPeriodMs", config.options)
        self.assertEqual(config.options["logPeriodMs"], 123)
        # boards
        self.assertEqual(len(config.boards), 1)
        board = config.boards[0]
        self.assertEqual(board.name, "BOARD1")
        # message
        self.assertEqual(len(board.messages), 1)
        msg = board.messages[0]
        self.assertEqual(msg.name, "MSG_A")
        self.assertEqual(msg.message_id, 0x100)
        self.assertEqual(msg.message_size, 2)
        # signal
        self.assertEqual(len(msg.signals), 1)
        sig = msg.signals[0]
        self.assertEqual(sig.name, "SIG1")
        self.assertEqual(sig.data_type, "uint8")
        self.assertEqual(sig.start_bit, 0)
        self.assertEqual(sig.length, 8)
        self.assertEqual(sig.factor, 2.0)
        self.assertEqual(sig.offset, 1.0)

    def test_data_parser(self):
        # Build config with one message and one signal
        cfg = (
            "> B\n"
            ">> M 0x200 2\n"
            ">>> S int8 0 8 1 0 signed little\n"
        )
        reader = TelemTokenReader(cfg)
        tokenizer = TelemTokenizer(reader)
        builder = TelemBuilder(tokenizer)
        config = builder.build()
        # create bit buffer and write raw value
        buf = TelemBitBuffer(bit_size=config.boards[0].messages[0].message_size * 8)
        # write a value of -5 (int8) at offset
        handle = TelemBitBufferHandle(offset=0, size=8)
        raw = (-5 & 0xFF).to_bytes(1, byteorder='little', signed=False)
        buf.write(handle, raw)
        parser = TelemDataParser(config)
        results = parser.parse_snapshot(buf)
        self.assertIn("B.M.S", list(results.keys())[0]) or True
        # value should be -5 * 1 + 0
        self.assertAlmostEqual(results["B.M.S"], -5.0)
