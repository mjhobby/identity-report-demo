import datetime
import os


class AgenaReport:
    """
    AgenaReport handles extracting data from Agena Report text files uploaded from the IGMSeq WebApp. Data extracted
    from this file includes identity_plate, identity_plate_well(s), and identity_marker(s)
    """
    READ_ONLY = 'r'
    UTF8 = 'utf-8'
    UNDERSCORE_DELIMITER = '_'
    DASH_DELIMITER = '-'
    TILDE_DELIMITER = '~'

    def __init__(self, fp):
        self.agena_report_fp = fp
        self.identity_plate = None
        self.current_plate = None
        self.identity_plate_wells = []
        self.identity_markers = {}

    def __str__(self):
        return 'The Agena Report {}'.format(self.agena_report_fp)

    def setup(self):
        if not os.path.isfile(self.agena_report_fp):
            raise RuntimeError('{} does not exist'.format(self.agena_report_fp))

    @staticmethod
    def extract_plate_label(line):
        """Retrieve the Plate Label value from the provided line of text

        Args:
            line (String): Line entry from the Agena Report

        Returns:
            (String) Plate label value
        """
        return line[:line.find('(')].strip() if line.find('(') > 0 else None

    @staticmethod
    def extract_plate_run_dttm(line):
        """Retrieve the date the Agena Report was run

        Args:
            line (String): Line entry from the Agena Report

        Returns:
            (datetime) Date in month/day/year format for when the Agena Report was run
        """
        return datetime.datetime.strptime(line[line.find(']') + 1:].strip(), '%m/%d/%Y') if line.find(']') > 0 else None

    @staticmethod
    def extract_alleles(line_elements):
        """Retrieve the sorted/formatted allelic values for line entries in the Agena Report

        Args:
            line_elements (List<String>): List of each element in the entry line

        Returns:
            (String) Alphabetically sorted allelic values from the entry line
        """
        alleles_element = line_elements[2]
        rs_id_element = line_elements[3].replace('-', '_')
        element_len = len(alleles_element)

        if element_len == 0:
            return ''
        elif element_len == 1 and rs_id_element in ['AMEL_XY', 'HSFY_2', 'XKRY_1']:
            return alleles_element
        elif element_len == 1:
            return alleles_element+alleles_element
        return ''.join(sorted(alleles_element))

    def extract_identity_plate_data(self, line):
        """Provided the entry line from the Agena Report, retrieve required elements for a new IdentityPlate
        model

        Args:
            line (String): String line entry from report

        Returns:
            (Dictionary) IdentityPlate model parameters and values
        """
        return {
            'filename': self.agena_report_fp,
            'plate_label': self.extract_plate_label(line),
            'run_dt': self.extract_plate_run_dttm(line)
        }

    def extract_plate_well_data(self, line_elements):
        """Provided the elements of a line from the report, extract data pertinent to be added as an IdentityPlateWell
        model object

        Args:
            line_elements (List<String>): list of string entries for elements in a report line

        Returns:
            (Dictionary) IdentityPlateWell model parameters and values
        """
        sample_label = line_elements[0]
        return {
            'plate_well': line_elements[4],
            'sample_label': sample_label
        }

    def extract_identity_marker_data(self, line_elements):
        """Provided the elements of a line from the report, extract data pertinent to be added as an
        IdentityAnalysisIdentityMarker model object

        Args:
            line_elements (List<String>): list of string entries for elements in a report line

        Returns:
            (Dictionary) IdentityAnalysisIdentityMarker model parameters and values
        """
        rs_id = line_elements[3].replace(self.DASH_DELIMITER, self.UNDERSCORE_DELIMITER)
        alleles = self.extract_alleles(line_elements)
        self.identity_markers[rs_id] = alleles

    def extract_line_contents(self, line):
        """Provided a line from the Agena Report file, convert entries to values in a list and add new values to list
        of identity_plate_wells and identity_markers

        Args:
            line (String): String line entry from report
        """
        line_elements = line.rstrip().split('\t')

        identity_plate_well = self.extract_plate_well_data(line_elements)
        if identity_plate_well not in self.identity_plate_wells:
            self.identity_plate_wells.append(identity_plate_well)
        self.extract_identity_marker_data(line_elements)

    def extract_contents(self):
        """Attempt to extract and store to the AgenaReport model parameters all required content as dictionary values
        from the Agena Report: the IdentityPlate model values, IdentityPlateWell(s), and
        IdentityAnalysisIdentityMarker(s)
        """
        column_header = False
        with open(self.agena_report_fp, self.READ_ONLY) as agena_report_file:
            for line in list(agena_report_file):
                if not self.identity_plate:
                    self.identity_plate = self.extract_identity_plate_data(line)
                    column_header = True
                elif column_header:
                    column_header = False
                else:
                    self.extract_line_contents(line)
