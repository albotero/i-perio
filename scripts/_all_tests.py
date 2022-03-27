#!/usr/bin/env python3

import unittest
from .test_grafico import TestGrafico
from .test_guardar_perio import TestGuardarPerio
from .test_main import TestPerio

def run_all_tests():
    test_classes_to_run = [
        TestGuardarPerio, TestGrafico, TestPerio
        ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

if __name__ == '__main__':
    run_all_tests()
