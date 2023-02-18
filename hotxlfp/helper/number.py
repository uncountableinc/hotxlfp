# -*- coding: utf-8 -*-
import torch

from .._compat import number_types, string_types

def to_number_wrapper(number):
    if isinstance(number, number_types):
        return number
    if isinstance(number, string_types):
        try:
            return int(number)
        except ValueError:
            try:
                return float(number)
            except ValueError:
                pass
    if isinstance(number, bool):
        return 1 if number else 0
    return number

def to_number(number, args = None):
    number = to_number_wrapper(number)
    if args is not None:
        args_list = list(args.values())
        if not (isinstance(number, torch.Tensor)) and len(args_list) > 0 and isinstance(args_list[0], torch.Tensor):
            return torch.ones_like(args_list[0]) * number
    return number


def invert_number(number):
    return -1 * to_number(number)
