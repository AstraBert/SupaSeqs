from kmer import kmer_featurization


class Encoder:
    def __init__(self):
        self.dna_encoder = kmer_featurization(5)

    def kmerize(self, seq):
        return self.dna_encoder.obtain_kmer_feature_for_one_sequence(
            seq, write_number_of_occurrences=False
        )
