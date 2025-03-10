import unittest

from hotxlfp import error
import torch
from hotxlfp import Parser
from math import pi
import numpy as np


def _test_equation(
    equation,
    variables,
    answer=None,
    should_fail=False,
):
    variable_tensors = {name: torch.tensor(value) for name, value in variables.items()}
    p = Parser(debug=True)
    try:
        func = p.parse(equation)["result"]
        result = func(variable_tensors)
    except (error.XLError, TypeError):
        assert should_fail
        return
    if isinstance(result, np.ndarray):
        assert (result == answer).all(), f"{result} != {answer}"
    else:
        assert isinstance(result, torch.Tensor)
        assert (
            torch.abs(result - torch.tensor(answer)) < 0.000001
        ).all(), f"{result} != {answer}"


class TestFormulaParser(unittest.TestCase):
    def test_plus(self):
        p = Parser(debug=True)
        func = p.parse("A + B + C")["result"]
        result = func({"A": 3.43, "B": 5.23, "C": 6.34})
        self.assertEqual(result, 15)

        p = Parser(debug=True)
        func = p.parse("SUM(A, B, SUM(3, C)) + 5")["result"]
        result = func({"A": 4, "B": 2, "C": 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse("SUM(A,, B, SUM(3, C)) + 5")["result"]
        result = func({"A": 4, "B": 2, "C": 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse("SUM(A;; B; SUM(3, C)) + 5")["result"]
        result = func({"A": 4, "B": 2, "C": 6})
        self.assertEqual(result, 20)

        p = Parser(debug=True)
        func = p.parse("MAX(A; B; 100) + MIN(A, B, C)")["result"]
        result = func({"A": 4.234, "B": 223, "C": 6})
        self.assertEqual(result, 223 + 4.234)

    def test_sqrt(self):
        p = Parser(debug=True)
        func = p.parse("SQRT(A)")["result"]
        result = func({"A": 16.0})
        self.assertEqual(result, 4)

        p = Parser(debug=True)
        func = p.parse("SQRT(100)")["result"]
        result = func({})
        self.assertEqual(result, 10)

    def test_if(self):
        p = Parser(debug=True)
        func = p.parse("IF(A < B, C, D)")["result"]
        result = func({"A": 2, "B": 3, "C": 4, "D": 5})
        self.assertEqual(result, 4)

        p = Parser(debug=True)
        func = p.parse("IF(A > B, C, D)")["result"]
        result = func({"A": 2, "B": 3, "C": 4, "D": 5})
        self.assertEqual(result, 5)

    def test_logical(self):
        p = Parser(debug=True)
        func = p.parse("100 > 10.0")["result"]
        result = func({})
        self.assertEqual(result, True)

        p = Parser(debug=True)
        func = p.parse("A > 10.0")["result"]
        result = func({"A": 100})
        self.assertEqual(result, True)

    def test_variable_name(self):
        p = Parser(debug=True)
        func = p.parse("a1")["result"]
        result = func({"a1": 5})
        self.assertEqual(result, 5)

    def test_array_add(self):
        p = Parser(debug=True)
        func = p.parse("a1 + 2")["result"]
        result = func({"a1": torch.tensor([4])})
        self.assertEqual(result, torch.tensor([6]))

        func = p.parse("a1 + a1")["result"]
        result = func({"a1": torch.tensor([4, 5])})
        assert (result == torch.tensor([8, 10])).all()

    def test_array_if(self):
        p = Parser(debug=True)
        func = p.parse("IF(a1 + a1 < 4, 1, 2)")["result"]
        result = torch.tensor(func({"a1": torch.tensor([1, 4])}))
        assert (result == torch.tensor([1, 2])).all().item()

        p = Parser(debug=True)
        func = p.parse("IF(3 < 4, a1, 2)")["result"]
        result = torch.tensor(func({"a1": torch.tensor([1, 2])}))
        assert (result == torch.tensor([1, 2])).all()

    def test_array_if_exp(self):
        p = Parser(debug=True)
        func = p.parse(
            "IF(((((a1+2)/3)*EXP(5)))<0.11, " + "(a1/2.2222),((( a1+9999)/33)*EXP(3)))"
        )["result"]
        input_vals = [1, 123, -432]
        answer = [
            6086.52634,
            6160.781962,
            -194.401944,
        ]
        result = torch.tensor(func({"a1": torch.tensor(input_vals)}))
        assert (torch.abs(result - torch.tensor(answer)) < 0.00001).all()

    def test_operation_on_if(self):
        p = Parser(debug=True)
        func = p.parse("IF(A<0.001234,A + 1, A + 2) - A")["result"]
        input_vals = [1, 123, -432]
        answer = [2, 2, 1]
        result = torch.tensor(func({"A": torch.tensor(input_vals)}))
        assert (torch.abs(result - torch.tensor(answer)) < 0.00001).all()

    def test_datatype(self):
        p = Parser(debug=True)
        func = p.parse("IF(T<50, A1, A2)")["result"]
        result = torch.tensor(
            func(
                {
                    "T": torch.tensor([10, 100]),
                    "A1": torch.tensor([20, 20], dtype=torch.double),
                    "A2": torch.tensor([30, 30], dtype=torch.int64),
                }
            )
        )
        assert (torch.abs(result - torch.tensor([20, 30])) < 0.00001).all()

    def test_array_or(self):
        p = Parser(debug=True)
        func = p.parse("IF(T <= 50, A1, A2)")["result"]
        result = torch.tensor(
            func(
                {
                    "T": torch.tensor([10, 50, 100]),
                    "A1": torch.tensor([20, 20, 20], dtype=torch.double),
                    "A2": torch.tensor([30, 30, 30], dtype=torch.int64),
                }
            )
        )
        assert (torch.abs(result - torch.tensor([20, 20, 30])) < 0.00001).all()

        func = p.parse("IF(T >= 50, A1, A2)")["result"]
        result = torch.tensor(
            func(
                {
                    "T": torch.tensor([10, 50, 100]),
                    "A1": torch.tensor([20, 20, 20], dtype=torch.double),
                    "A2": torch.tensor([30, 30, 30], dtype=torch.int64),
                }
            )
        )
        assert (torch.abs(result - torch.tensor([30, 20, 20])) < 0.00001).all()

    def test_average(self):
        p = Parser(debug=True)
        func = p.parse("((100 - a1) / 100) * AVERAGE(a2)")["result"]
        result = func({"a1": torch.tensor([4]), "a2": torch.tensor([5])})
        assert (torch.abs(result - torch.tensor([4.8])) < 0.00001).all()

        p = Parser(debug=True)
        func = p.parse("AVERAGE(a1, a2, a2)")["result"]
        result = func({"a1": torch.tensor([2, 4, 8]), "a2": torch.tensor([3, 4, 5])})
        assert (torch.abs(result - torch.tensor([2.66666666, 4, 6])) < 0.000001).all()

    def test_min_max_array(self):
        p = Parser(debug=True)
        func = p.parse("MIN(a1, a2)")["result"]
        result = func({"a1": torch.tensor([5, 5, 5]), "a2": torch.tensor([1, 10, 5])})
        assert (torch.abs(result - torch.tensor([1, 5, 5])) < 0.00001).all()

        p = Parser(debug=True)
        func = p.parse("MAX(a1, a2)")["result"]
        result = func({"a1": torch.tensor([5, 5, 5]), "a2": torch.tensor([1, 10, 5])})
        assert (torch.abs(result - torch.tensor([5, 10, 5])) < 0.00001).all()

    def test_log(self):
        p = Parser(debug=True)
        func = p.parse("LOG(a1)")["result"]
        result = func({"a1": torch.exp(torch.tensor([5, 23.234]))})
        assert (torch.abs(result - torch.tensor([5, 23.234])) < 0.00001).all()

        func = p.parse("LN(a1)")["result"]
        result = func({"a1": torch.exp(torch.tensor([5, 23.234]))})
        assert (torch.abs(result - torch.tensor([5, 23.234])) < 0.00001).all()

        func = p.parse("LOG(a1, 10)")["result"]
        result = func({"a1": 10 ** (torch.tensor([5, 23.234]))})
        assert (torch.abs(result - torch.tensor([5, 23.234])) < 0.00001).all()

        func = p.parse("LOG10(a1)")["result"]
        result = func({"a1": 10 ** (torch.tensor([5, 23.234]))})
        assert (torch.abs(result - torch.tensor([5, 23.234])) < 0.00001).all()

        _test_equation(
            equation="LOG(a1 / a2)",
            variables={"a1": [1, 2], "a2": [2, 3]},
            answer=[torch.log(torch.tensor(1 / 2)), torch.log(torch.tensor(2 / 3))],
        )
        _test_equation(
            equation="LOG(123)",
            variables={"a1": [1]},
            answer=[torch.log(torch.tensor(123))],
        )

    def test_trailing_decimal(self):
        _test_equation(equation="1.", variables={"a1": [1]}, answer=[1])
        _test_equation(equation="1. + 1", variables={"a1": [1]}, answer=[2])
        _test_equation(equation="SQRT(1.)", variables={"a1": [1]}, answer=[1])
        _test_equation(equation="1 + 1.", variables={"a1": [1]}, answer=[2])
        _test_equation(equation="1.2", variables={"a1": [1]}, answer=[1.2])

    def test_exponent(self):
        _test_equation(equation="a1 ^ a1", variables={"a1": [1, 2]}, answer=[1, 4])
        _test_equation(equation="3 ^ a1", variables={"a1": [1, 2]}, answer=[3, 9])
        _test_equation(equation="a1 ^ 3", variables={"a1": [1, 2]}, answer=[1, 8])
        _test_equation(equation="3 ^ 3", variables={"a1": [1, 2]}, answer=[27, 27])

    def test_tan(self):
        _test_equation(
            equation="TAN(a1)", variables={"a1": [pi, pi / 4]}, answer=[0, 1]
        )
        _test_equation(equation="TAN(a1)", variables={"a1": [0]}, answer=[0])

    def test_negative(self):
        _test_equation(equation="-a1", variables={"a1": [5]}, answer=[-5])
        _test_equation(equation="-5", variables={"a1": [5]}, answer=[-5])
        _test_equation(equation="-(-5)", variables={"a1": [5]}, answer=[5])

    def test_function_space(self):
        _test_equation(equation="LOG(1)", variables={"a1": [1]}, answer=[0])
        _test_equation(equation="LOG (1)", variables={"a1": [1]}, answer=[0])
        _test_equation(equation="LOG  (1)", variables={"a1": [1]}, answer=[0])
        _test_equation(equation="   LOG  (  1 ) ", variables={"a1": [1]}, answer=[0])

    def test_implicit_multiplication(self):
        _test_equation(equation="1 + (a1) + 1", variables={"a1": [2]}, answer=[4])
        _test_equation(equation="(a1)", variables={"a1": [2]}, answer=[2])
        _test_equation(
            equation="a1 (a2) ",
            variables={"a1": [2, 2.5], "a2": [3, 3]},
            answer=[6, 7.5],
        )
        _test_equation(
            equation="a1( a2 ) ",
            variables={"a1": [2, 2.5], "a2": [3, 3]},
            answer=[6, 7.5],
        )
        _test_equation(
            equation="a1(a2 ) ",
            variables={"a1": [2, 2.5], "a2": [3, 3]},
            answer=[6, 7.5],
        )
        _test_equation(
            equation="a1(a2) ",
            variables={"a1": [2, 2.5], "a2": [3, 3]},
            answer=[6, 7.5],
        )
        _test_equation(
            equation="5(a1)(a2)(a2) ", variables={"a1": [2], "a2": [3]}, answer=[90]
        )
        _test_equation(
            equation="(5(a1 + 5))((a2)(a2) + 5) ",
            variables={"a1": [2], "a2": [3]},
            answer=[490],
        )
        _test_equation(
            equation="(5(SQRT(a1 + 2)))(SQRT(a2)(a2) + 5) ",
            variables={"a1": [2], "a2": [4]},
            answer=[130],
        )
        _test_equation(
            equation="  ( 5 (  SQRT   (a1 + 2)))( SQRT(a2)   (a2) + 5) ",
            variables={"a1": [2], "a2": [4]},
            answer=[130],
        )
        _test_equation(equation="a1(a2)", variables={"a1": [1], "a2": [2]}, answer=[2])
        _test_equation(equation="SQRT(4(4))", variables={"a1": [1]}, answer=[4])
        _test_equation(equation="4(SQRT(4(4)))", variables={"a1": [1]}, answer=[16])
        _test_equation(
            equation="SQRT(4(SQRT(4(4))))", variables={"a1": [1]}, answer=[4]
        )

        _test_equation(equation="( 200 / 1 ) - 1", variables={"a1": [1]}, answer=[199])
        _test_equation(
            equation="( ( 200 ) / 1 ) - 1", variables={"a1": [1]}, answer=[199]
        )
        _test_equation(
            equation="( ( 200 ) / 1 ) - (1)", variables={"a1": [1]}, answer=[199]
        )
        _test_equation(
            equation="( ( 200 ) / 1 ) - (-1)", variables={"a1": [1]}, answer=[201]
        )
        _test_equation(
            equation="( ( 200 ) / 1 )(-1)", variables={"a1": [1]}, answer=[-200]
        )
        _test_equation(
            equation="( ( 200 ) / 1 )(-(-1))", variables={"a1": [1]}, answer=[200]
        )
        _test_equation(
            equation="10 - ( 200 / 1 )", variables={"a1": [1]}, answer=[-190]
        )
        _test_equation(
            equation="(10 * -10) - ( 200 / 1 )", variables={"a1": [1]}, answer=[-300]
        )
        _test_equation(equation="1 / -a1", variables={"a1": [5]}, answer=[-1 / 5])
        _test_equation(equation="-1 / -a1", variables={"a1": [5]}, answer=[1 / 5])
        _test_equation(equation="(a1 / a1) - a1", variables={"a1": [5]}, answer=[-4])
        _test_equation(equation="a1 / a1 - a1", variables={"a1": [5]}, answer=[-4])
        _test_equation(equation="-a1 (a1) -a1", variables={"a1": [5]}, answer=[-30])

    def test_decimal(self):
        _test_equation(equation=".99", variables={"a1": [1]}, answer=[0.99])
        _test_equation(equation="a1/.99", variables={"a1": [1]}, answer=[1 / 0.99])
        _test_equation(equation="a1/.99", variables={"a1": [1]}, answer=[1 / 0.99])
        _test_equation(equation="a1/0.99", variables={"a1": [1]}, answer=[1 / 0.99])
        _test_equation(
            equation="a1 + .9+.9", variables={"a1": [1]}, answer=[1 + 0.9 + 0.9]
        )
        _test_equation(
            equation="a1 + .009/.099*.009 - a1",
            variables={"a1": [1]},
            answer=[1 + 0.009 / 0.099 * 0.009 - 1],
        )

    def test_order_of_operations(self):
        _test_equation(equation="2^-2-1", variables={"a1": [1]}, answer=[-0.75])
        _test_equation(equation="(2^(-1))", variables={"a1": [1]}, answer=[0.5])
        _test_equation(equation="((2^(-1))-1)", variables={"a1": [1]}, answer=[-0.5])
        _test_equation(equation="2^2-1", variables={"a1": [1]}, answer=[3])
        _test_equation(equation="2^((-1)-1)", variables={"a1": [1]}, answer=[0.25])
        _test_equation(equation="2/((-1)-1)", variables={"a1": [1]}, answer=[-1])
        _test_equation(equation="2*((-1)-1)", variables={"a1": [1]}, answer=[-4])
        _test_equation(equation="2+((-1)-1)", variables={"a1": [1]}, answer=[0])
        _test_equation(equation="(2^1-1)", variables={"a1": [1]}, answer=[1])
        _test_equation(equation="(2^(-1)-1)", variables={"a1": [1]}, answer=[-0.5])
        _test_equation(equation="1 + 2 * 3 - 4", variables={"a1": [1]}, answer=[3])

    def test_if_statement_args(self):
        _test_equation(
            equation="IF(a1 > 10, 1, 100, 400)", variables={"a1": [4]}, should_fail=True
        )
        _test_equation(
            equation="IF(a1 > 10, 400)", variables={"a1": [4]}, should_fail=True
        )
        _test_equation(
            equation="IF(a1 > 10, )", variables={"a1": [4]}, should_fail=True
        )
        _test_equation(equation="IF(,, )", variables={"a1": [4]}, should_fail=True)
        _test_equation(
            equation="IF(a1 > 100, 40, IF(a1 > 1, 4, 56))",
            variables={"a1": [40]},
            answer=[4],
        )
        _test_equation(
            equation="IF(a1 > 10, 40, IF(a1 > 10, 4))",
            variables={"a1": [4]},
            should_fail=True,
        )
        _test_equation(
            equation="IF(a1 > 10, 'abc', 'def')", variables={"a1": [4]}, answer=["def"]
        )
        _test_equation(
            equation="IF(a1 > 100, 'abc', IF(a1 > 1, 4, 56))",
            variables={"a1": [40]},
            answer=["4.0"],
        )

    def test_tensors(self):
        _test_equation(
            equation="MIN(a1 * 2, 2, 23, a1)", variables={"a1": [5]}, answer=[2]
        )
        _test_equation(equation="MIN(2, a1 * 2)", variables={"a1": [5]}, answer=[2])
        _test_equation(equation="MAX(a1 * 2, 2)", variables={"a1": [5]}, answer=[10])
        _test_equation(equation="MAX(2, a1 * 2)", variables={"a1": [5]}, answer=[10])
        _test_equation(
            equation="MAX(MAX(2, a1 * 2), 100)",
            variables={"a1": [5, 4]},
            answer=[100, 100],
        )
        _test_equation(equation="5", variables={"a1": [5, 4]}, answer=[5])
        _test_equation(equation="SQRT(100)", variables={"a1": [5]}, answer=[10])
        _test_equation(
            equation="CEILING(a1)", variables={"a1": [4.5, -1.2]}, answer=[5, -1]
        )
        _test_equation(
            equation="CEILING(a1, a2)",
            variables={"a1": [0.5, 0.5], "a2": [1, 2]},
            answer=[1, 2],
        )
        _test_equation(
            equation="CEILING(a1, a2)",
            variables={"a1": [0.5, 0.5], "a2": [2]},
            answer=[2, 2],
        )
        _test_equation(
            equation="CEILING(a1, a2)", variables={"a1": [0.5], "a2": [1]}, answer=[1]
        )
        _test_equation(
            equation="IF(a1 <> a2, 1, 0)",
            variables={"a1": [3, 2], "a2": [3, 3]},
            answer=[0, 1],
        )
        _test_equation(
            equation="IF(a1 <> a2, 1, 0)", variables={"a1": 4, "a2": 2}, answer=1
        )
        _test_equation(
            equation="IF(a1 < a2, 1, 0)",
            variables={"a1": [1, 2], "a2": [0, 0]},
            answer=[0, 0],
        )
        _test_equation(
            equation="IF(a1 < a2, 1, 0)", variables={"a1": 2, "a2": 3}, answer=1
        )

    def test_scientific_notation(self):
        _test_equation(equation="2e2", variables={"a1": [1.1]}, answer=[200])
        _test_equation(equation="5(m)", variables={"m": [10]}, answer=[50])
        _test_equation(equation="5(e)", variables={"e": [10]}, answer=[50])
        _test_equation(equation="5(evar)", variables={"evar": [10]}, answer=[50])
        _test_equation(equation="5(vare)", variables={"vare": [10]}, answer=[50])
        _test_equation(equation="1 e 2", variables={"a1": [1.1]}, answer=[100])
        _test_equation(equation="1e2", variables={"a1": [1.1]}, answer=[100])
        _test_equation(equation="2*1e2", variables={"a1": [1.1]}, answer=[200])
        _test_equation(equation="2*1e2^3", variables={"a1": [1.1]}, answer=[2000000])
        _test_equation(equation="(2*1e2)^3", variables={"a1": [1.1]}, answer=[8000000])
        _test_equation(
            equation="(2)e(4)",
            variables={"a1": [1.1]},
            answer=[8000000],
            should_fail=True,
        )
        _test_equation(equation="(2)e(4)", variables={"a1": [1.1]}, should_fail=True)
        _test_equation(equation="0.2e2", variables={"a1": [1.1]}, answer=20)
        _test_equation(
            equation="0.2e0.2", variables={"a1": [1.1]}, answer=0.2 * (10**0.2)
        )
        _test_equation(equation="2e-1", variables={"a1": [1.1]}, answer=0.2)
        _test_equation(equation="-2e1", variables={"a1": [1.1]}, answer=-20)
        _test_equation(equation="-2e-1", variables={"a1": [1.1]}, answer=-0.2)
        _test_equation(
            equation="-2e-.1", variables={"a1": [1.1]}, answer=-2 * (10 ** (-0.1))
        )

        _test_equation(equation="2E2", variables={"a1": [1.1]}, answer=[200])
        _test_equation(equation="2*1E2", variables={"a1": [1.1]}, answer=[200])
        _test_equation(equation="0.2E2", variables={"a1": [1.1]}, answer=20)
        _test_equation(equation="-2E-1", variables={"a1": [1.1]}, answer=-0.2)


if __name__ == "__main__":
    unittest.main()
