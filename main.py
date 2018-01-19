import argparse
import math
import time
from modules.CandidateFinder import CandidateFinder
from modules.BamHandler import BamHandler
from modules.FastaHandler import FastaHandler

"""
alignmentPolish finds possible variant sites in given bam file.

It requires three parameters:
- bam_file_path: path to a bam file
- reference_file_path: path to a reference file

Creates:
- CandidateFinder object that contains windows of possible variants.
"""

class View:
    """
    Works as a main class and handles user interaction with different modules.
    """
    def __init__(self, chromosome_name, bam_file_path, reference_file_path):
        # --- initialize handlers ---
        self.bam_handler = BamHandler(bam_file_path)
        self.fasta_handler = FastaHandler(reference_file_path)

        # --- initialize parameters ---
        self.chromosome_name = chromosome_name

    def parse_window(self, start_position, end_position):
        """
        Find possible candidate windows.
        """
        reads = self.bam_handler.get_reads(chromosome_name=self.chromosome_name,
                                           start=start_position,
                                           stop=end_position)

        candidate_finder = CandidateFinder(reads=reads,
                                           fasta_handler=self.fasta_handler,
                                           chromosome_name=self.chromosome_name,
                                           window_start_position=start_position,
                                           window_end_position=end_position)
        # parse reads to find candidate positions
        candidate_finder.parse_reads(reads=reads)
        # merge candidate positions to windows
        candidate_finder.merge_positions()
        # print the windows we got
        candidate_finder.print_windows()

    def test(self):
        self.parse_window(start_position=100000, end_position=200000)

    def do_parallel(self, max_threads=5):
        """
        Split the chromosome into different ranges for parallel processing.
        :param max_threads: Maximum number of threads to create
        :return:
        """
        # entire length of chromosome
        whole_length = self.fasta_handler.get_chr_sequence_length(self.chromosome_name)
        # expected length of each segment
        each_segment_length = int(math.ceil(whole_length / max_threads))

        for i in range(max_threads):
            print(i*each_segment_length, (i+1)*each_segment_length + 1000)

            start_time = time.time()

            # parse window of the segment. Use a 1000 overlap for corner cases.
            self.parse_window(i*each_segment_length, (i+1)*each_segment_length + 1000)

            end_time = time.time()
            print("Total time: ", end_time-start_time)
            exit()


if __name__ == '__main__':
    '''
    Processes arguments and performs tasks to generate the pileup.
    '''
    parser = argparse.ArgumentParser()
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument(
        "--ref",
        type=str,
        required=True,
        help="Reference corresponding to the BAM file."
    )
    parser.add_argument(
        "--bam",
        type=str,
        required=True,
        help="BAM file containing reads of interest."
    )
    parser.add_argument(
        "--chromosome_name",
        type=str,
        default="3",
        help="Desired chromosome number E.g.: 3"
    )
    parser.add_argument(
        "--max_threads",
        type=int,
        default=5,
        help="Number of maximum threads for this region."
    )

    FLAGS, unparsed = parser.parse_known_args()

    view = View(chromosome_name=FLAGS.chromosome_name,
                bam_file_path=FLAGS.bam,
                reference_file_path=FLAGS.ref)

    # view.do_parallel(max_threads=FLAGS.max_threads)
    view.test()

# usage example:
# python3 main.py --bam /Users/saureous/data/chr3_200k.bam --ref /Users/saureous/data/chr3.fa --chromosome_name chr3 --window_size 1000