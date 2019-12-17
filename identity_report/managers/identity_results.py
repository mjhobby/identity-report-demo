import itertools
import time
import os

from ..report_handler import AgenaReport, IdentityMarkerVcf
from ..test_files import test_data_dir, test_files

CHECKMARK = u'\u2713'


class IdentityResultManager(object):
    def __init__(self):
        super(IdentityResultManager, self).__init__()

    def build_comparison_key(self):
        output = '\t_________________________KEY_______________________________\n'
        output += '\t\t\tMatching Results      : \033[92m{}\033[0m\n'.format(CHECKMARK)
        output += '\t\t\tHeterozygous Mismatch : \033[93m/\033[0m\n'
        output += '\t\t\tHomozygous Mismatch   : \033[91mX\033[0m\n'
        output += '\t\t\tNo Call               : -\n'
        output += '\t___________________________________________________________\n'
        return output

    def extract_file_identity_results(self, test_file_indices):
        os.system("clear")
        all_test_files = test_files
        indices = test_file_indices.split(',')
        test_files_selected = []
        for index in indices:
            if int(index) > len(all_test_files):
                print('Invalid index provided for test file: {}'.format(index))
                time.sleep(3)
                return None
            test_files_selected.append(os.path.join(test_data_dir, all_test_files[int(index)-1]))
        samples = []
        identity_results = {}
        for result_file in test_files_selected:
            if result_file.endswith('.txt'):
                report = AgenaReport(fp=result_file)
                report.setup()
                report.extract_contents()
                sample_label = report.identity_plate_wells[0]['sample_label']
                if sample_label not in samples:
                    samples.append(sample_label)
                    identity_results[sample_label] = {}
                identity_results[sample_label]['Agena'] = report.identity_markers
            elif result_file.endswith('.vcf'):
                report = IdentityMarkerVcf(identity_marker_vcf_fp=result_file)
                report.setup()
                report.parse_content()
                if report.sample_label not in samples:
                    samples.append(report.sample_label)
                    identity_results[report.sample_label] = {}
                identity_results[report.sample_label]['VCF'] = report.identity_marker_calls
        for sample in samples:
            if 'Agena' in identity_results[sample].keys() and 'VCF' in identity_results[sample].keys():
                print('Performing Agena to VCF Identity Result Comparisons for {}:\n'
                      '___________________________________________________________\n'.format(sample))
                self.output_sample_validation_results(identity_results[sample]['Agena'], identity_results[sample]['VCF'])

        for combination in list(itertools.combinations(samples, 2)):
            sample_a = combination[0]
            sample_b = combination[1]
            self.output_multi_sample_comparisons(sample_a, sample_b, identity_results)

        os.system("clear")
        print('Comparisons done. Returning to home menu...')
        time.sleep(2)

    @staticmethod
    def run_comparisons(results_a, results_b):
        output = ''
        for rs_id in results_a.keys():
            comparison_match = '-'
            agena_alleles = results_a[rs_id]
            formatted_rs_id = rs_id if len(rs_id) >= 8 else rs_id + ' '.join(['' for i in range(9 - len(rs_id))])
            new_line = '{}:\t\t{}\t\t'.format(formatted_rs_id, agena_alleles if agena_alleles else '00')
            vcf_alleles = '00'
            if rs_id in results_b.keys():
                vcf_alleles = results_b[rs_id]
                if agena_alleles == vcf_alleles:
                    comparison_match = '\033[92m{}\033[0m'.format(CHECKMARK)
                elif agena_alleles[0] in vcf_alleles or agena_alleles[1] in vcf_alleles:
                    comparison_match = '\033[93m/\033[0m'
                else:
                    comparison_match = '\033[91mX\033[0m'
            output += '{}{}\t{}\n'.format(new_line, vcf_alleles, comparison_match)
        return output

    def output_sample_validation_results(self, agena_results, vcf_results):
        output = self.build_comparison_key()
        output += 'Agena to VCF Identity Result Comparisons:\n\n'
        output += 'Marker Location /\tAgena Results /\tVCF Results\n'
        output += self.run_comparisons(agena_results, vcf_results)
        print(output)
        input('Press any key to move on to next comparison...')

    def output_multi_sample_comparisons(self, sample_a, sample_b, identity_results):
        sample_a_results = identity_results[sample_a]
        sample_b_results = identity_results[sample_b]
        sample_a_report_types = list(sample_a_results.keys())
        sample_b_report_types = list(sample_b_results.keys())

        if 'Agena' in sample_a_report_types and 'Agena' in sample_b_report_types:
            output = self.build_comparison_key()
            output += 'Comparing {} Agena results with {} Agena results\n\n'.format(sample_a, sample_b)
            output += 'marker location\t\t{}\t{}\n'.format(sample_a, sample_b)
            output += self.run_comparisons(sample_a_results['Agena'], sample_b_results['Agena'])
            print(output)
            input('Press any key to move on to next comparison...')
        os.system("clear")

        if 'VCF' in sample_a_report_types and 'VCF' in sample_b_report_types:
            output = 'Comparing {} VCF results with {} VCF results\n\n'.format(sample_a, sample_b)
            output += 'marker location\t\t{}\t{}\n'.format(sample_a, sample_b)
            output += self.run_comparisons(sample_a_results['VCF'], sample_b_results['VCF'])
            print(output)
            input('Press any key to move on to next comparison...')
        os.system("clear")
