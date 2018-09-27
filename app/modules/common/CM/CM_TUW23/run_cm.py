import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW23.f0_main_call as f0


def main(case_study, pixT, DHT, gfa_path, hdm_path, output_dir):
    output_summary = f0.main(case_study, pixT, DHT, gfa_path, hdm_path,
                             output_dir)
    return output_summary
