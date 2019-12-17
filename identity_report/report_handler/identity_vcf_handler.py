import os


class IdentityMarkerVcf:
    """IdentityMarkerVcf parses provided Identity Marker VCF file to retrieve variant call records and then, using
    a dictionary of Identity Marker values provided, retrieve the Identity Marker data from the parsed file content.
    """

    class IdentityMarkerVcfContentProcessor:
        """IdentityMarkerVcf processes provided line content from the IdentityMarkerVcf file in such a way that
        key content can quickly be determined/retained and used by the parent IdentityMarkerVcf object.
        """
        GENOTYPE = ('GT', 'genotype')
        GENOTYPE_QUALITY = ('GQ', 'genotype_quality')
        GENOTYPE_LIKLIHOOD = ('PL', 'genotype_liklihood')
        ALLELIC_DEPTH = ('AD', 'allelic_depth')
        ALT_ALLELE_COUNT = ('AC', 'alt_allele_count')
        ALT_ALLELE_FREQ = ('AF', 'alt_allele_freq')
        TOT_ALLELE_COUNT = ('AN', 'total_allele_count')
        DBSNP_MEMBER = ('DB', 'dbsnp_member')
        READ_DEPTH = ('DP', 'read_depth')
        SPAN_DEL_FRACT = ('Dels', 'spanning_deletions_fraction')
        FISHER_BIAS_FRACT = ('FS', 'fisher_strand_bias_test_fraction')
        LARGEST_CON_HRUN = ('HRun', 'largest_continuous_homopolymer_run')
        HAP_SCORE = ('HaplotypeScore', 'haplotype_score')
        MAP_QUAL = ('MQ', 'mapping_quality')
        MAP_QUAL0 = ('MQ0', 'mapping_quality_zero_reads')
        QUAL_DEPTH = ('QD', 'quality_by_depth')
        STRAND_BIAS = ('SB', 'strand_bias')
        VAR_DIST_BIAS = ('VDB',
                         'variant_distance_bias')  # ID=VDB,Number=1,Type=Float,Description="Variant Distance Bias (v2) for filtering splice-site artefacts in RNA-seq data. Note: this version may be broken."
        READ_POS_BIAS = ('RPB', 'read_position_bias')  # ID=RPB,Number=1,Type=Float,Description="Read Position Bias"
        AF1 = ('AF1',
               'AF1')  # ID=AF1,Number=1,Type=Float,Description="Max-likelihood estimate of the first ALT allele frequency (assuming HWE)"
        AC1 = ('AC1',
               'AC1')  # ID=AC1,Number=1,Type=Float,Description="Max-likelihood estimate of the first ALT allele count (no HWE assumption)"
        DP4 = ('DP4',
               'DP4')  # ID=DP4,Number=4,Type=Integer,Description="# high-quality ref-forward bases, ref-reverse, alt-forward and alt-reverse bases"
        FQ = ('FQ', 'FQ')  # ID=FQ,Number=1,Type=Float,Description="Phred probability of all samples being the same"
        PV4 = ('PV4',
               'PV4')  # ID=PV4,Number=4,Type=Float,Description="P-values for strand bias, baseQ bias, mapQ bias and tail distance bias"

        OPT_VCF_ATTR_LIST = [
            GENOTYPE, GENOTYPE_QUALITY, GENOTYPE_LIKLIHOOD, ALLELIC_DEPTH, ALT_ALLELE_COUNT, ALT_ALLELE_FREQ,
            TOT_ALLELE_COUNT, DBSNP_MEMBER, READ_DEPTH, SPAN_DEL_FRACT, FISHER_BIAS_FRACT, LARGEST_CON_HRUN, HAP_SCORE,
            MAP_QUAL, MAP_QUAL0, QUAL_DEPTH, STRAND_BIAS, VAR_DIST_BIAS, READ_POS_BIAS, AF1, AC1, DP4, FQ, PV4
        ]

        def __init__(self, line):
            [chrom, position, rs_id, ref_allele, alt_allele, qual,
             filter_line_value, info_text, format_text, value_text] = line.strip().split('\t')

            self.chrom = chrom
            self.position = position
            self.rs_id = rs_id
            self.ref_allele = ref_allele
            self.alt_allele = alt_allele
            self.qual = qual
            self.filter_line_value = filter_line_value

            # Defaults for optional fields
            for optional_attr in self.OPT_VCF_ATTR_LIST:
                setattr(self, optional_attr[0], None)
            self.dbsnp_member = False

            for pair_string in info_text.split(';'):
                key_value_list = pair_string.split('=')
                key = key_value_list[0]
                if len(key_value_list) == 2:
                    value = key_value_list[1]
                else:
                    value = True  # This is a bit field, so just give it a True value
                self.set_vcf_attr_by_key_value(key, value)

            format_items = format_text.split(':')
            value_items = value_text.split(':')
            for i in range(len(format_items)):
                self.set_vcf_attr_by_key_value(format_items[i], value_items[i])

        def __str__(self):
            return 'VCF line containing: chrom {} ; position {}; rs_id {}; ref_allele {}; alt_allele {}'.format(
                self.chrom, self.position, self.rs_id, self.ref_allele, self.alt_allele
            )

        def set_vcf_attr_by_key_value(self, key, value):
            try:
                attribute = {}
                for opt_vcf_attr in self.OPT_VCF_ATTR_LIST:
                    attribute[opt_vcf_attr[0]] = opt_vcf_attr[1]
                setattr(self, attribute[key], value)
            except KeyError:
                raise RuntimeError('VcfLine.set_vcf_attr_by_key_value - key error: {}'.format(key))

        def get_alleles(self):
            """
            Construct the combined alleles string.  The alleles will be in alphebetic order if het.

            Returns:
                (String) Genotype Allelic combination
            """
            # Check if reference call
            if self.alt_allele == '.':
                return self.get_ref_call()

            alleles = [self.ref_allele, self.alt_allele]
            return ''.join(sorted(alleles))

        def get_ref_call(self):
            """Get the referecne call quality by examining the read depth score.
                Read depth >= 20 is scored at 99
                Read depth < 20 is scored at the actual read depth value

            Returns:
                (String) Duplicated Reference Allele
            """
            return self.ref_allele + self.ref_allele

        def get_het_w_ref(self):
            """Get the heterozygote allelic combination by combining the reference allele with the alt allele

            Returns:
                (String) Reference Allele and Alt Allele combined
            """
            # Hetero with reference
            return ''.join(sorted(self.ref_allele + self.alt_allele))

        def get_het_w_out_ref(self):
            """Get the heterozygote allelic combination w/out ref allel by combining the alt allele at
            position 0 with the alt allele at position 2

            Returns:
                (String) Alt Allele character at position 0 and Alt Allele character at position 2
            """
            # Hetero WITHOUT reference
            return ''.join(sorted(self.alt_allele[0] + self.alt_allele[2]))

        def get_hom_not_ref(self):
            """Get the homozygote allelic combination by combining the alt allele with itself

            Returns:
                (String) Alt Allele duplicated for Homozygote value
            """
            # Homozygote, not reference
            return self.alt_allele + self.alt_allele

    def __init__(self, identity_marker_vcf_fp):
        # File local/destination file path parameters
        self.identity_marker_vcf_fp = identity_marker_vcf_fp
        self.contents = []
        self.identity_marker_calls = {}
        self.sample_label = None
        self.identity_markers = {
            '1:000001': 'rs000001',
            '1:000002': 'rs000002',
            '2:000003': 'rs000003',
            '2:000004': 'rs000004',
            '2:000005': 'rs000005',
            '2:000006': 'rs000006',
            '3:000007': 'rs000007',
            '3:000008': 'rs000008',
            '4:000009': 'rs000009',
            '5:000010': 'rs000010',
            '5:000011': 'rs000011',
            '5:000012': 'rs000012',
            '6:000013': 'rs000013',
            '7:000014': 'rs000014',
            '8:000015': 'rs000015',
            '8:000016': 'rs000016',
            '9:000017': 'rs000017',
            '9:000018': 'rs000018',
            '11:000019': 'rs000019',
            '12:000020': 'rs000020',
            '12:000021': 'rs000021',
            '13:000022': 'rs000022',
            '13:000023': 'rs000023',
            '14:000024': 'rs000024',
            '19:000025': 'rs000025',
            '19:000026': 'rs000026',
            '21:000027': 'rs000027',
            '21:000028': 'rs000028',
            '22:000029': 'rs000029',
            '22:000030': 'rs000030'
        }

    def __str__(self):
        return 'Identity Marker VCF {}'.format(self.identity_marker_vcf_fp)

    def setup(self):
        """Download the BAM file that will be used to generate the Identity Marker VCF file as well as
        set up the new local copy of the Identity Marker VCF.
        """
        if not os.path.isfile(self.identity_marker_vcf_fp):
            raise RuntimeError('{} does not exist'.format(self.identity_marker_vcf_fp))

    def parse_content(self):
        """Parse the Identity Marker VCF file contents

        Returns:
            (List) Each entry in the Identity Marker VCF file
        """
        with open(self.identity_marker_vcf_fp, 'r') as f:
            for vcf_line in f:
                if vcf_line[0] == '#':
                    contents = vcf_line.strip().split('\t')
                    if contents[0] == '#CHROM':
                        self.sample_label = contents[-1]
                    continue
                self.contents.append(vcf_line.rstrip())
        self.extract_identity_markers()

    def extract_identity_markers(self):
        """Extract variants found in Identity Marker VCF file that match Identity Marker
        positions

        Args:
            identity_markers (List<String>): identity marker values
        """
        for vcf_line in self.contents:
            formatted_vcf_line = self.IdentityMarkerVcfContentProcessor(vcf_line.rstrip())
            variant_key = self.identity_markers.get('{}:{}'.format(formatted_vcf_line.chrom, formatted_vcf_line.position))

            self.identity_marker_calls[variant_key] = formatted_vcf_line.get_alleles()
