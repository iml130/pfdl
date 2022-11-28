# Generated from PFDLLexer.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys

if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


from antlr_denter.DenterHelper import DenterHelper
from pfdl_scheduler.parser.PFDLParser import PFDLParser


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2?")
        buf.write("\u01a7\b\1\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6")
        buf.write("\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r")
        buf.write("\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22")
        buf.write("\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30")
        buf.write("\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35")
        buf.write('\4\36\t\36\4\37\t\37\4 \t \4!\t!\4"\t"\4#\t#\4$\t$\4')
        buf.write("%\t%\4&\t&\4'\t'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t")
        buf.write("-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63")
        buf.write("\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4")
        buf.write(":\t:\4;\t;\4<\t<\4=\t=\4>\t>\3\2\3\2\3\2\3\2\3\2\3\2\3")
        buf.write("\2\3\3\3\3\3\3\3\3\3\3\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\6")
        buf.write("\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7\3\b\3\b\3\b\3")
        buf.write("\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n\3\n")
        buf.write("\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13")
        buf.write("\3\f\3\f\3\f\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\3")
        buf.write("\r\3\16\3\16\3\16\3\16\3\17\3\17\3\17\3\17\3\17\3\17\3")
        buf.write("\17\3\20\3\20\3\20\3\20\3\20\3\20\3\20\3\21\3\21\3\21")
        buf.write("\3\21\3\21\3\21\3\21\3\21\3\22\3\22\3\22\3\22\3\22\3\23")
        buf.write("\3\23\3\23\3\23\3\23\3\23\3\24\3\24\3\25\3\25\3\26\3\26")
        buf.write("\3\27\3\27\3\27\3\27\3\30\3\30\3\31\3\31\3\32\3\32\3\33")
        buf.write("\3\33\6\33\u00ff\n\33\r\33\16\33\u0100\3\33\3\33\3\34")
        buf.write("\6\34\u0106\n\34\r\34\16\34\u0107\3\34\3\34\3\35\5\35")
        buf.write("\u010d\n\35\3\35\3\35\7\35\u0111\n\35\f\35\16\35\u0114")
        buf.write('\13\35\3\36\3\36\3\37\3\37\3 \3 \3!\3!\3!\3"\3"\3#\3')
        buf.write("#\3#\3$\3$\3$\3%\3%\3%\3&\3&\3&\3&\3'\3'\3'\3(\3(\3")
        buf.write(")\3)\3*\3*\3+\3+\3,\3,\3-\6-\u013c\n-\r-\16-\u013d\3.")
        buf.write("\3.\3.\3.\3/\3/\3/\3/\7/\u0148\n/\f/\16/\u014b\13/\3/")
        buf.write("\3/\3\60\3\60\7\60\u0151\n\60\f\60\16\60\u0154\13\60\3")
        buf.write("\61\3\61\7\61\u0158\n\61\f\61\16\61\u015b\13\61\3\62\3")
        buf.write("\62\3\62\3\62\7\62\u0161\n\62\f\62\16\62\u0164\13\62\3")
        buf.write("\62\3\62\3\63\3\63\3\64\3\64\3\65\3\65\6\65\u016e\n\65")
        buf.write("\r\65\16\65\u016f\3\65\3\65\3\66\3\66\3\67\3\67\38\38")
        buf.write("\39\59\u017b\n9\39\39\39\69\u0180\n9\r9\169\u0181\59\u0184")
        buf.write("\n9\39\59\u0187\n9\3:\3:\3:\7:\u018c\n:\f:\16:\u018f\13")
        buf.write(":\5:\u0191\n:\3;\3;\5;\u0195\n;\3;\3;\3<\6<\u019a\n<\r")
        buf.write("<\16<\u019b\3<\3<\3=\3=\3=\3=\3>\3>\3>\3>\4\u0149\u0162")
        buf.write("\2?\4\5\6\6\b\7\n\b\f\t\16\n\20\13\22\f\24\r\26\16\30")
        buf.write('\17\32\20\34\21\36\22 \23"\24$\25&\26(\27*\30,\31.\32')
        buf.write("\60\33\62\34\64\35\66\368\37: <!>\"@#B$D%F&H'J(L)N*P")
        buf.write("+R,T-V.X/Z\60\\\61^\62`\63b\64d\65f\66h\67j8l9n:p;r<t")
        buf.write('\2v\2x=z>|?\4\2\3\f\3\2\f\f\4\2\13\13""\3\2\62;\3\2')
        buf.write("c|\6\2\62;C\\aac|\3\2C\\\3\2\63;\4\2GGgg\4\2--//\5\2\13")
        buf.write('\f\17\17""\2\u01b7\2\4\3\2\2\2\2\6\3\2\2\2\2\b\3\2\2')
        buf.write("\2\2\n\3\2\2\2\2\f\3\2\2\2\2\16\3\2\2\2\2\20\3\2\2\2\2")
        buf.write("\22\3\2\2\2\2\24\3\2\2\2\2\26\3\2\2\2\2\30\3\2\2\2\2\32")
        buf.write('\3\2\2\2\2\34\3\2\2\2\2\36\3\2\2\2\2 \3\2\2\2\2"\3\2')
        buf.write("\2\2\2$\3\2\2\2\2&\3\2\2\2\2(\3\2\2\2\2*\3\2\2\2\2,\3")
        buf.write("\2\2\2\2.\3\2\2\2\2\60\3\2\2\2\2\62\3\2\2\2\2\64\3\2\2")
        buf.write("\2\2\66\3\2\2\2\28\3\2\2\2\2:\3\2\2\2\2<\3\2\2\2\2>\3")
        buf.write("\2\2\2\2@\3\2\2\2\2B\3\2\2\2\2D\3\2\2\2\2F\3\2\2\2\2H")
        buf.write("\3\2\2\2\2J\3\2\2\2\2L\3\2\2\2\2N\3\2\2\2\2P\3\2\2\2\2")
        buf.write("R\3\2\2\2\2T\3\2\2\2\2V\3\2\2\2\2X\3\2\2\2\2Z\3\2\2\2")
        buf.write("\2\\\3\2\2\2\2^\3\2\2\2\2`\3\2\2\2\2b\3\2\2\2\3d\3\2\2")
        buf.write("\2\3f\3\2\2\2\3h\3\2\2\2\3j\3\2\2\2\3l\3\2\2\2\3n\3\2")
        buf.write("\2\2\3p\3\2\2\2\3r\3\2\2\2\3x\3\2\2\2\3z\3\2\2\2\3|\3")
        buf.write("\2\2\2\4~\3\2\2\2\6\u0085\3\2\2\2\b\u008a\3\2\2\2\n\u008d")
        buf.write("\3\2\2\2\f\u0091\3\2\2\2\16\u0096\3\2\2\2\20\u009c\3\2")
        buf.write("\2\2\22\u009f\3\2\2\2\24\u00a8\3\2\2\2\26\u00b2\3\2\2")
        buf.write("\2\30\u00b9\3\2\2\2\32\u00c0\3\2\2\2\34\u00c7\3\2\2\2")
        buf.write('\36\u00cb\3\2\2\2 \u00d2\3\2\2\2"\u00d9\3\2\2\2$\u00e1')
        buf.write("\3\2\2\2&\u00e6\3\2\2\2(\u00ec\3\2\2\2*\u00ee\3\2\2\2")
        buf.write(",\u00f0\3\2\2\2.\u00f2\3\2\2\2\60\u00f6\3\2\2\2\62\u00f8")
        buf.write("\3\2\2\2\64\u00fa\3\2\2\2\66\u00fc\3\2\2\28\u0105\3\2")
        buf.write("\2\2:\u010c\3\2\2\2<\u0115\3\2\2\2>\u0117\3\2\2\2@\u0119")
        buf.write("\3\2\2\2B\u011b\3\2\2\2D\u011e\3\2\2\2F\u0120\3\2\2\2")
        buf.write("H\u0123\3\2\2\2J\u0126\3\2\2\2L\u0129\3\2\2\2N\u012d\3")
        buf.write("\2\2\2P\u0130\3\2\2\2R\u0132\3\2\2\2T\u0134\3\2\2\2V\u0136")
        buf.write("\3\2\2\2X\u0138\3\2\2\2Z\u013b\3\2\2\2\\\u013f\3\2\2\2")
        buf.write("^\u0143\3\2\2\2`\u014e\3\2\2\2b\u0155\3\2\2\2d\u015c\3")
        buf.write("\2\2\2f\u0167\3\2\2\2h\u0169\3\2\2\2j\u016b\3\2\2\2l\u0173")
        buf.write("\3\2\2\2n\u0175\3\2\2\2p\u0177\3\2\2\2r\u017a\3\2\2\2")
        buf.write("t\u0190\3\2\2\2v\u0192\3\2\2\2x\u0199\3\2\2\2z\u019f\3")
        buf.write("\2\2\2|\u01a3\3\2\2\2~\177\7U\2\2\177\u0080\7v\2\2\u0080")
        buf.write("\u0081\7t\2\2\u0081\u0082\7w\2\2\u0082\u0083\7e\2\2\u0083")
        buf.write("\u0084\7v\2\2\u0084\5\3\2\2\2\u0085\u0086\7V\2\2\u0086")
        buf.write("\u0087\7c\2\2\u0087\u0088\7u\2\2\u0088\u0089\7m\2\2\u0089")
        buf.write("\7\3\2\2\2\u008a\u008b\7K\2\2\u008b\u008c\7p\2\2\u008c")
        buf.write("\t\3\2\2\2\u008d\u008e\7Q\2\2\u008e\u008f\7w\2\2\u008f")
        buf.write("\u0090\7v\2\2\u0090\13\3\2\2\2\u0091\u0092\7N\2\2\u0092")
        buf.write("\u0093\7q\2\2\u0093\u0094\7q\2\2\u0094\u0095\7r\2\2\u0095")
        buf.write("\r\3\2\2\2\u0096\u0097\7Y\2\2\u0097\u0098\7j\2\2\u0098")
        buf.write("\u0099\7k\2\2\u0099\u009a\7n\2\2\u009a\u009b\7g\2\2\u009b")
        buf.write("\17\3\2\2\2\u009c\u009d\7V\2\2\u009d\u009e\7q\2\2\u009e")
        buf.write("\21\3\2\2\2\u009f\u00a0\7R\2\2\u00a0\u00a1\7c\2\2\u00a1")
        buf.write("\u00a2\7t\2\2\u00a2\u00a3\7c\2\2\u00a3\u00a4\7n\2\2\u00a4")
        buf.write("\u00a5\7n\2\2\u00a5\u00a6\7g\2\2\u00a6\u00a7\7n\2\2\u00a7")
        buf.write("\23\3\2\2\2\u00a8\u00a9\7E\2\2\u00a9\u00aa\7q\2\2\u00aa")
        buf.write("\u00ab\7p\2\2\u00ab\u00ac\7f\2\2\u00ac\u00ad\7k\2\2\u00ad")
        buf.write("\u00ae\7v\2\2\u00ae\u00af\7k\2\2\u00af\u00b0\7q\2\2\u00b0")
        buf.write("\u00b1\7p\2\2\u00b1\25\3\2\2\2\u00b2\u00b3\7R\2\2\u00b3")
        buf.write("\u00b4\7c\2\2\u00b4\u00b5\7u\2\2\u00b5\u00b6\7u\2\2\u00b6")
        buf.write("\u00b7\7g\2\2\u00b7\u00b8\7f\2\2\u00b8\27\3\2\2\2\u00b9")
        buf.write("\u00ba\7H\2\2\u00ba\u00bb\7c\2\2\u00bb\u00bc\7k\2\2\u00bc")
        buf.write("\u00bd\7n\2\2\u00bd\u00be\7g\2\2\u00be\u00bf\7f\2\2\u00bf")
        buf.write("\31\3\2\2\2\u00c0\u00c1\7Q\2\2\u00c1\u00c2\7p\2\2\u00c2")
        buf.write("\u00c3\7F\2\2\u00c3\u00c4\7q\2\2\u00c4\u00c5\7p\2\2\u00c5")
        buf.write("\u00c6\7g\2\2\u00c6\33\3\2\2\2\u00c7\u00c8\7G\2\2\u00c8")
        buf.write("\u00c9\7p\2\2\u00c9\u00ca\7f\2\2\u00ca\35\3\2\2\2\u00cb")
        buf.write("\u00cc\7p\2\2\u00cc\u00cd\7w\2\2\u00cd\u00ce\7o\2\2\u00ce")
        buf.write("\u00cf\7d\2\2\u00cf\u00d0\7g\2\2\u00d0\u00d1\7t\2\2\u00d1")
        buf.write("\37\3\2\2\2\u00d2\u00d3\7u\2\2\u00d3\u00d4\7v\2\2\u00d4")
        buf.write("\u00d5\7t\2\2\u00d5\u00d6\7k\2\2\u00d6\u00d7\7p\2\2\u00d7")
        buf.write("\u00d8\7i\2\2\u00d8!\3\2\2\2\u00d9\u00da\7d\2\2\u00da")
        buf.write("\u00db\7q\2\2\u00db\u00dc\7q\2\2\u00dc\u00dd\7n\2\2\u00dd")
        buf.write("\u00de\7g\2\2\u00de\u00df\7c\2\2\u00df\u00e0\7p\2\2\u00e0")
        buf.write("#\3\2\2\2\u00e1\u00e2\7v\2\2\u00e2\u00e3\7t\2\2\u00e3")
        buf.write("\u00e4\7w\2\2\u00e4\u00e5\7g\2\2\u00e5%\3\2\2\2\u00e6")
        buf.write("\u00e7\7h\2\2\u00e7\u00e8\7c\2\2\u00e8\u00e9\7n\2\2\u00e9")
        buf.write("\u00ea\7u\2\2\u00ea\u00eb\7g\2\2\u00eb'\3\2\2\2\u00ec")
        buf.write("\u00ed\7<\2\2\u00ed)\3\2\2\2\u00ee\u00ef\7\60\2\2\u00ef")
        buf.write("+\3\2\2\2\u00f0\u00f1\7.\2\2\u00f1-\3\2\2\2\u00f2\u00f3")
        buf.write("\7}\2\2\u00f3\u00f4\3\2\2\2\u00f4\u00f5\b\27\2\2\u00f5")
        buf.write("/\3\2\2\2\u00f6\u00f7\7$\2\2\u00f7\61\3\2\2\2\u00f8\u00f9")
        buf.write("\7]\2\2\u00f9\63\3\2\2\2\u00fa\u00fb\7_\2\2\u00fb\65\3")
        buf.write("\2\2\2\u00fc\u00fe\7%\2\2\u00fd\u00ff\n\2\2\2\u00fe\u00fd")
        buf.write("\3\2\2\2\u00ff\u0100\3\2\2\2\u0100\u00fe\3\2\2\2\u0100")
        buf.write("\u0101\3\2\2\2\u0101\u0102\3\2\2\2\u0102\u0103\b\33\3")
        buf.write("\2\u0103\67\3\2\2\2\u0104\u0106\t\3\2\2\u0105\u0104\3")
        buf.write("\2\2\2\u0106\u0107\3\2\2\2\u0107\u0105\3\2\2\2\u0107\u0108")
        buf.write("\3\2\2\2\u0108\u0109\3\2\2\2\u0109\u010a\b\34\3\2\u010a")
        buf.write("9\3\2\2\2\u010b\u010d\7\17\2\2\u010c\u010b\3\2\2\2\u010c")
        buf.write("\u010d\3\2\2\2\u010d\u010e\3\2\2\2\u010e\u0112\7\f\2\2")
        buf.write('\u010f\u0111\7"\2\2\u0110\u010f\3\2\2\2\u0111\u0114\3')
        buf.write("\2\2\2\u0112\u0110\3\2\2\2\u0112\u0113\3\2\2\2\u0113;")
        buf.write("\3\2\2\2\u0114\u0112\3\2\2\2\u0115\u0116\7*\2\2\u0116")
        buf.write("=\3\2\2\2\u0117\u0118\7+\2\2\u0118?\3\2\2\2\u0119\u011a")
        buf.write("\7>\2\2\u011aA\3\2\2\2\u011b\u011c\7>\2\2\u011c\u011d")
        buf.write("\7?\2\2\u011dC\3\2\2\2\u011e\u011f\7@\2\2\u011fE\3\2\2")
        buf.write("\2\u0120\u0121\7@\2\2\u0121\u0122\7?\2\2\u0122G\3\2\2")
        buf.write("\2\u0123\u0124\7?\2\2\u0124\u0125\7?\2\2\u0125I\3\2\2")
        buf.write("\2\u0126\u0127\7#\2\2\u0127\u0128\7?\2\2\u0128K\3\2\2")
        buf.write("\2\u0129\u012a\7C\2\2\u012a\u012b\7p\2\2\u012b\u012c\7")
        buf.write("f\2\2\u012cM\3\2\2\2\u012d\u012e\7Q\2\2\u012e\u012f\7")
        buf.write("t\2\2\u012fO\3\2\2\2\u0130\u0131\7#\2\2\u0131Q\3\2\2\2")
        buf.write("\u0132\u0133\7,\2\2\u0133S\3\2\2\2\u0134\u0135\7\61\2")
        buf.write("\2\u0135U\3\2\2\2\u0136\u0137\7/\2\2\u0137W\3\2\2\2\u0138")
        buf.write("\u0139\7-\2\2\u0139Y\3\2\2\2\u013a\u013c\t\4\2\2\u013b")
        buf.write("\u013a\3\2\2\2\u013c\u013d\3\2\2\2\u013d\u013b\3\2\2\2")
        buf.write("\u013d\u013e\3\2\2\2\u013e[\3\2\2\2\u013f\u0140\5Z-\2")
        buf.write("\u0140\u0141\7\60\2\2\u0141\u0142\5Z-\2\u0142]\3\2\2\2")
        buf.write("\u0143\u0149\7$\2\2\u0144\u0145\7^\2\2\u0145\u0148\7$")
        buf.write("\2\2\u0146\u0148\13\2\2\2\u0147\u0144\3\2\2\2\u0147\u0146")
        buf.write("\3\2\2\2\u0148\u014b\3\2\2\2\u0149\u014a\3\2\2\2\u0149")
        buf.write("\u0147\3\2\2\2\u014a\u014c\3\2\2\2\u014b\u0149\3\2\2\2")
        buf.write("\u014c\u014d\7$\2\2\u014d_\3\2\2\2\u014e\u0152\t\5\2\2")
        buf.write("\u014f\u0151\t\6\2\2\u0150\u014f\3\2\2\2\u0151\u0154\3")
        buf.write("\2\2\2\u0152\u0150\3\2\2\2\u0152\u0153\3\2\2\2\u0153a")
        buf.write("\3\2\2\2\u0154\u0152\3\2\2\2\u0155\u0159\t\7\2\2\u0156")
        buf.write("\u0158\t\6\2\2\u0157\u0156\3\2\2\2\u0158\u015b\3\2\2\2")
        buf.write("\u0159\u0157\3\2\2\2\u0159\u015a\3\2\2\2\u015ac\3\2\2")
        buf.write("\2\u015b\u0159\3\2\2\2\u015c\u0162\7$\2\2\u015d\u015e")
        buf.write("\7^\2\2\u015e\u0161\7$\2\2\u015f\u0161\13\2\2\2\u0160")
        buf.write("\u015d\3\2\2\2\u0160\u015f\3\2\2\2\u0161\u0164\3\2\2\2")
        buf.write("\u0162\u0163\3\2\2\2\u0162\u0160\3\2\2\2\u0163\u0165\3")
        buf.write("\2\2\2\u0164\u0162\3\2\2\2\u0165\u0166\7$\2\2\u0166e\3")
        buf.write("\2\2\2\u0167\u0168\7<\2\2\u0168g\3\2\2\2\u0169\u016a\7")
        buf.write("$\2\2\u016ai\3\2\2\2\u016b\u016d\7%\2\2\u016c\u016e\n")
        buf.write("\2\2\2\u016d\u016c\3\2\2\2\u016e\u016f\3\2\2\2\u016f\u016d")
        buf.write("\3\2\2\2\u016f\u0170\3\2\2\2\u0170\u0171\3\2\2\2\u0171")
        buf.write("\u0172\b\65\3\2\u0172k\3\2\2\2\u0173\u0174\7]\2\2\u0174")
        buf.write("m\3\2\2\2\u0175\u0176\7_\2\2\u0176o\3\2\2\2\u0177\u0178")
        buf.write("\7.\2\2\u0178q\3\2\2\2\u0179\u017b\7/\2\2\u017a\u0179")
        buf.write("\3\2\2\2\u017a\u017b\3\2\2\2\u017b\u017c\3\2\2\2\u017c")
        buf.write("\u0183\5t:\2\u017d\u017f\7\60\2\2\u017e\u0180\t\4\2\2")
        buf.write("\u017f\u017e\3\2\2\2\u0180\u0181\3\2\2\2\u0181\u017f\3")
        buf.write("\2\2\2\u0181\u0182\3\2\2\2\u0182\u0184\3\2\2\2\u0183\u017d")
        buf.write("\3\2\2\2\u0183\u0184\3\2\2\2\u0184\u0186\3\2\2\2\u0185")
        buf.write("\u0187\5v;\2\u0186\u0185\3\2\2\2\u0186\u0187\3\2\2\2\u0187")
        buf.write("s\3\2\2\2\u0188\u0191\7\62\2\2\u0189\u018d\t\b\2\2\u018a")
        buf.write("\u018c\t\4\2\2\u018b\u018a\3\2\2\2\u018c\u018f\3\2\2\2")
        buf.write("\u018d\u018b\3\2\2\2\u018d\u018e\3\2\2\2\u018e\u0191\3")
        buf.write("\2\2\2\u018f\u018d\3\2\2\2\u0190\u0188\3\2\2\2\u0190\u0189")
        buf.write("\3\2\2\2\u0191u\3\2\2\2\u0192\u0194\t\t\2\2\u0193\u0195")
        buf.write("\t\n\2\2\u0194\u0193\3\2\2\2\u0194\u0195\3\2\2\2\u0195")
        buf.write("\u0196\3\2\2\2\u0196\u0197\5t:\2\u0197w\3\2\2\2\u0198")
        buf.write("\u019a\t\13\2\2\u0199\u0198\3\2\2\2\u019a\u019b\3\2\2")
        buf.write("\2\u019b\u0199\3\2\2\2\u019b\u019c\3\2\2\2\u019c\u019d")
        buf.write("\3\2\2\2\u019d\u019e\b<\3\2\u019ey\3\2\2\2\u019f\u01a0")
        buf.write("\7}\2\2\u01a0\u01a1\3\2\2\2\u01a1\u01a2\b=\2\2\u01a2{")
        buf.write("\3\2\2\2\u01a3\u01a4\7\177\2\2\u01a4\u01a5\3\2\2\2\u01a5")
        buf.write("\u01a6\b>\4\2\u01a6}\3\2\2\2\30\2\3\u0100\u0107\u010c")
        buf.write("\u0112\u013d\u0147\u0149\u0152\u0159\u0160\u0162\u016f")
        buf.write("\u017a\u0181\u0183\u0186\u018d\u0190\u0194\u019b\5\7\3")
        buf.write("\2\b\2\2\6\2\2")
        return buf.getvalue()


class PFDLLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    JSON = 1

    INDENT = 1
    DEDENT = 2
    STRUCT = 3
    TASK = 4
    IN = 5
    OUT = 6
    LOOP = 7
    WHILE = 8
    TO = 9
    PARALLEL = 10
    CONDITION = 11
    PASSED = 12
    FAILED = 13
    ON_DONE = 14
    END = 15
    NUMBER_P = 16
    STRING_P = 17
    BOOLEAN_P = 18
    TRUE = 19
    FALSE = 20
    COLON = 21
    DOT = 22
    COMMA = 23
    JSON_OPEN = 24
    QUOTE = 25
    ARRAY_LEFT = 26
    ARRAY_RIGHT = 27
    COMMENT = 28
    WHITESPACE = 29
    NL = 30
    LEFT_PARENTHESIS = 31
    RIGHT_PARENTHESIS = 32
    LESS_THAN = 33
    LESS_THAN_OR_EQUAL = 34
    GREATER_THAN = 35
    GREATER_THAN_OR_EQUAL = 36
    EQUAL = 37
    NOT_EQUAL = 38
    BOOLEAN_AND = 39
    BOOLEAN_OR = 40
    BOOLEAN_NOT = 41
    STAR = 42
    SLASH = 43
    MINUS = 44
    PLUS = 45
    INTEGER = 46
    FLOAT = 47
    STRING = 48
    STARTS_WITH_LOWER_C_STR = 49
    STARTS_WITH_UPPER_C_STR = 50
    JSON_STRING = 51
    JSON_COLON = 52
    JSON_QUOTE = 53
    JSON_COMMENT = 54
    JSON_ARRAY_LEFT = 55
    JSON_ARRAY_RIGHT = 56
    JSON_COMMA = 57
    NUMBER = 58
    WS = 59
    JSON_OPEN_2 = 60
    JSON_CLOSE = 61

    channelNames = ["DEFAULT_TOKEN_CHANNEL", "HIDDEN"]

    modeNames = ["DEFAULT_MODE", "JSON"]

    literalNames = [
        "<INVALID>",
        "'Struct'",
        "'Task'",
        "'In'",
        "'Out'",
        "'Loop'",
        "'While'",
        "'To'",
        "'Parallel'",
        "'Condition'",
        "'Passed'",
        "'Failed'",
        "'OnDone'",
        "'End'",
        "'number'",
        "'string'",
        "'boolean'",
        "'true'",
        "'false'",
        "'.'",
        "'('",
        "')'",
        "'<'",
        "'<='",
        "'>'",
        "'>='",
        "'=='",
        "'!='",
        "'And'",
        "'Or'",
        "'!'",
        "'*'",
        "'/'",
        "'-'",
        "'+'",
        "'}'",
    ]

    symbolicNames = [
        "<INVALID>",
        "INDENT",
        "DEDENT",
        "STRUCT",
        "TASK",
        "IN",
        "OUT",
        "LOOP",
        "WHILE",
        "TO",
        "PARALLEL",
        "CONDITION",
        "PASSED",
        "FAILED",
        "ON_DONE",
        "END",
        "NUMBER_P",
        "STRING_P",
        "BOOLEAN_P",
        "TRUE",
        "FALSE",
        "COLON",
        "DOT",
        "COMMA",
        "JSON_OPEN",
        "QUOTE",
        "ARRAY_LEFT",
        "ARRAY_RIGHT",
        "COMMENT",
        "WHITESPACE",
        "NL",
        "LEFT_PARENTHESIS",
        "RIGHT_PARENTHESIS",
        "LESS_THAN",
        "LESS_THAN_OR_EQUAL",
        "GREATER_THAN",
        "GREATER_THAN_OR_EQUAL",
        "EQUAL",
        "NOT_EQUAL",
        "BOOLEAN_AND",
        "BOOLEAN_OR",
        "BOOLEAN_NOT",
        "STAR",
        "SLASH",
        "MINUS",
        "PLUS",
        "INTEGER",
        "FLOAT",
        "STRING",
        "STARTS_WITH_LOWER_C_STR",
        "STARTS_WITH_UPPER_C_STR",
        "JSON_STRING",
        "JSON_COLON",
        "JSON_QUOTE",
        "JSON_COMMENT",
        "JSON_ARRAY_LEFT",
        "JSON_ARRAY_RIGHT",
        "JSON_COMMA",
        "NUMBER",
        "WS",
        "JSON_OPEN_2",
        "JSON_CLOSE",
    ]

    ruleNames = [
        "STRUCT",
        "TASK",
        "IN",
        "OUT",
        "LOOP",
        "WHILE",
        "TO",
        "PARALLEL",
        "CONDITION",
        "PASSED",
        "FAILED",
        "ON_DONE",
        "END",
        "NUMBER_P",
        "STRING_P",
        "BOOLEAN_P",
        "TRUE",
        "FALSE",
        "COLON",
        "DOT",
        "COMMA",
        "JSON_OPEN",
        "QUOTE",
        "ARRAY_LEFT",
        "ARRAY_RIGHT",
        "COMMENT",
        "WHITESPACE",
        "NL",
        "LEFT_PARENTHESIS",
        "RIGHT_PARENTHESIS",
        "LESS_THAN",
        "LESS_THAN_OR_EQUAL",
        "GREATER_THAN",
        "GREATER_THAN_OR_EQUAL",
        "EQUAL",
        "NOT_EQUAL",
        "BOOLEAN_AND",
        "BOOLEAN_OR",
        "BOOLEAN_NOT",
        "STAR",
        "SLASH",
        "MINUS",
        "PLUS",
        "INTEGER",
        "FLOAT",
        "STRING",
        "STARTS_WITH_LOWER_C_STR",
        "STARTS_WITH_UPPER_C_STR",
        "JSON_STRING",
        "JSON_COLON",
        "JSON_QUOTE",
        "JSON_COMMENT",
        "JSON_ARRAY_LEFT",
        "JSON_ARRAY_RIGHT",
        "JSON_COMMA",
        "NUMBER",
        "INT",
        "EXP",
        "WS",
        "JSON_OPEN_2",
        "JSON_CLOSE",
    ]

    grammarFileName = "PFDLLexer.g4"

    def __init__(self, input=None, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(
            self, self.atn, self.decisionsToDFA, PredictionContextCache()
        )
        self._actions = None
        self._predicates = None

    class PFDLDenter(DenterHelper):
        def __init__(self, lexer, nl_token, indent_token, dedent_token, ignore_eof):
            super().__init__(nl_token, indent_token, dedent_token, ignore_eof)
            self.lexer: PFDLLexer = lexer

        def pull_token(self):
            return super(PFDLLexer, self.lexer).nextToken()

    denter = None

    def nextToken(self):
        if not self.denter:
            self.denter = self.PFDLDenter(
                self, self.NL, PFDLLexer.INDENT, PFDLLexer.DEDENT, ignore_eof=False
            )
        return self.denter.next_token()
