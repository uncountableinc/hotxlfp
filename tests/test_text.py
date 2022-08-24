# -*- coding: utf-8 -*-
import unittest
import math
from hotxlfp import Parser
from hotxlfp.formulas.error import XLError, DIV_ZERO, VALUE


class TestText(unittest.TestCase):

    def test_char(self):
        p = Parser(debug=True)
        ret = p.parse('CHAR(65)')
        self.assertEqual(ret['result']({}), 'A')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHAR(33)')
        self.assertEqual(ret['result']({}), '!')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CHAR(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)

    def test_code(self):
        p = Parser(debug=True)
        ret = p.parse('CODE("A")')
        self.assertEqual(ret['result']({}), 65)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CODE("!")')
        self.assertEqual(ret['result']({}), 33)
        self.assertEqual(ret['error'], None)

    def test_clean(self):
        p = Parser(debug=True)
        ret = p.parse('CLEAN(CHAR(9)&"Monthly report"&CHAR(10))')
        self.assertEqual(ret['result']({}), 'Monthly report')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CLEAN(B3)')
        self.assertEqual(ret['result']({"B3": ""}), '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('CLEAN(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)
        ret = p.parse('CLEAN(223)')
        self.assertEqual(ret['result']({}), '223')
        self.assertEqual(ret['error'], None)

    def test_concatenate(self):
        p = Parser(debug=True)
        ret = p.parse('CONCAT("The"," ","sun"," ","will"," ","come"," ","up"," ","tomorrow.")')
        self.assertEqual(ret['result']({}), 'The sun will come up tomorrow.')
        self.assertEqual(ret['error'], None)

    def test_len(self):
        p = Parser(debug=True)
        ret = p.parse('LEN("Phoenix, AZ")')
        self.assertEqual(ret['result']({}), 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN("     One   ")')
        self.assertEqual(ret['result']({}), 11)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(B3)')
        self.assertEqual(ret['result']({ "B3": "" }), 0)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(3)')
        self.assertEqual(ret['result']({}), 1)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(223)')
        self.assertEqual(ret['result']({}), 3)
        self.assertEqual(ret['error'], None)
        ret = p.parse('LEN(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)


    def test_lower(self):
        p = Parser(debug=True)
        ret = p.parse('LOWER("aBcDe")')
        self.assertEqual(ret['result']({}), 'abcde')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(B3)')
        self.assertEqual(ret['result']({"B3": ""}), '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(223)')
        self.assertEqual(ret['result']({}), '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('LOWER(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)

    def test_upper(self):
        p = Parser(debug=True)
        ret = p.parse('UPPER("aBcDe")')
        self.assertEqual(ret['result']({}), 'ABCDE')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(B3)')
        self.assertEqual(ret['result']({"B3":""}), '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(223)')
        self.assertEqual(ret['result']({}), '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('UPPER(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)

    def test_proper(self):
        p = Parser(debug=True)
        ret = p.parse('PROPER("aBcDe")')
        self.assertEqual(ret['result']({}), 'Abcde')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER("76budGet")')
        self.assertEqual(ret['result']({}), '76Budget')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(B3)')
        self.assertEqual(ret['result']({"B3":""}), '')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(223)')
        self.assertEqual(ret['result']({}), '223')
        self.assertEqual(ret['error'], None)
        ret = p.parse('PROPER(1/0)')
        self.assertEqual(ret['result']({}), DIV_ZERO)
        self.assertEqual(ret['error'], None)

    def test_substitute(self):
        p = Parser(debug=True)
        ret = p.parse('SUBSTITUTE("ccc", "a", "b")')
        self.assertEqual(ret['result']({}), 'ccc')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ccc", "a", "b", 2)')
        self.assertEqual(ret['result']({}), 'ccc')
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b")')
        self.assertEqual(ret['result']({}), "olb b todos e todbs bs meninbs e os meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", 2)')
        self.assertEqual(ret['result']({}), "ola b todos e todas as meninas e os meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", 0)')
        self.assertEqual(ret['result']({}), VALUE)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "os", "a", 3)')
        self.assertEqual(ret['result']({}), "ola a todos e todas as meninas e os menina")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "os", "a", 2)')
        self.assertEqual(ret['result']({}), "ola a todos e todas as meninas e a meninos")
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE("ola a todos e todas as meninas e os meninos", "a", "b", "a")')
        self.assertEqual(ret['result']({}), VALUE)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE(, "a", "b", "a")')
        self.assertEqual(ret['result']({}), VALUE)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE(;;)')
        self.assertEqual(ret['result']({}), None)
        self.assertEqual(ret['error'], None)
        ret = p.parse('SUBSTITUTE(;;;)')
        self.assertEqual(ret['result']({}), VALUE)
        self.assertEqual(ret['error'], None)

    def test_textjoin(self):
        p = Parser(debug=True)
        ret = p.parse('TEXTJOIN(";", TRUE, {"1";"2";"3"})')
        self.assertEqual(ret['result']({"TRUE": 1}), '1;2;3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXTJOIN(";", TRUE, {"1",,"2","3"})')
        self.assertEqual(ret['result']({"TRUE":1}), '1;2;3')
        ret = p.parse('TEXTJOIN(";", FALSE, {"1",,"2","3"})')
        self.assertEqual(ret['result']({"FALSE":0}), '1;;2;3')
        self.assertEqual(ret['error'], None)
        ret = p.parse('TEXTJOIN(1, FALSE, {"1",,"2","3"})')
        self.assertEqual(ret['result']({"FALSE":0}), VALUE)
        self.assertEqual(ret['error'], None)
