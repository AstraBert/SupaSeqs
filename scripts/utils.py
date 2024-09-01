from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import sessionmaker
import warnings
from Bio import SeqIO
import gzip


class ErrorOccuredWarning(Warning):
    """An error occured but it was handled by try...except"""


class SupaClient:
    def __init__(self, connection_string: str):
        """
        Initialize a Client instance.

        Args:
            connection_string (str): A string representing the database connection information.

        Returns:
            None
        """
        self.engine = create_engine(connection_string)
        self.meta = MetaData(schema="public")
        self.Session = sessionmaker(self.engine)

        with self.Session() as sess:
            with sess.begin():
                sess.execute(text("create schema if not exists public;"))

    def execute_query(self, query):
        try:
            with self.Session() as sess:
                with sess.begin():
                    res = sess.execute(text(query))
            return res
        except Exception as e:
            warnings.warn(f"An error occurred: {e}", ErrorOccuredWarning)
            return None

    def disconnect(self) -> None:
        """
        Disconnect the client from the database.

        Returns:
            None
        """
        self.engine.dispose()
        return


def load_data(infile):
    """
    Load data from infile if it is in fastq format (after having unzipped it, if it is zipped)

    Parameters:
        infile (str): Path to the input file.

    Returns:
        dict or bool: Dictionary containing sequence information if successful, False otherwise.
    """
    try:
        if infile.endswith(".gz"):  # If file is gzipped, unzip it
            y = gzip.open(infile, "rt", encoding="latin-1")
            if (
                infile.endswith(".fasta.gz")
                or infile.endswith(".fa.gz")
                or infile.endswith(".fas.gz")
                or infile.endswith(".fna.gz")
            ):
                # Read file as fasta if it is fasta
                records = SeqIO.parse(y, "fasta")
                seq_dict = {}  # Create a dictionary to store everything from the file
                for record in records:
                    # Update dictionary with header as key, sequence as value
                    seq_dict.update({record.id: str(record.seq)})
                y.close()
                return seq_dict
        # Read file directly as fasta if it is not zipped fastq
        elif (
            infile.endswith(".fasta")
            or infile.endswith(".fa")
            or infile.endswith(".fas")
            or infile.endswith(".fna")
        ):
            with open(infile, "r") as y:
                records = SeqIO.parse(y, "fasta")
                seq_dict = {}  # Create a dictionary to store everything from the file
                for record in records:
                    # Update dictionary with header as key, sequence as value
                    seq_dict.update({record.id: str(record.seq)})
                y.close()
                return seq_dict
        else:
            raise ValueError("File is the wrong format")
    except FileNotFoundError as e:
        warnings.warn(f"An error occurred: {e}", ErrorOccuredWarning)
        return None
