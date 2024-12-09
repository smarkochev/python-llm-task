from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd
import typer
import re

# Logger
import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# Set logger level
logger.setLevel(logging.DEBUG)

# Start interactive console
app = typer.Typer(no_args_is_help=True)

@app.command()
def extract(input_filename: str='regulations.txt', output_filename: str='extracted_requirements.json') -> None:
    """
    Extract sections from regulations file, simulate LLM integration and save output results

    :param input_filename: Path to a regulations text file
    :param output_filename: Path to an output (json or csv) file
    :returns: Output results are saved as either a json or a csv file
    """
    regulation_summary = RegulationRequirements(input_filename, output_filename)
    regulation_summary.extract_and_summarize()


@dataclass
class RegulationRequirements:
    """
    Class to extract sections from regulations text file and prepare summaries.

    :param input_filename: Path to a regulations text file
    :param output_filename: Path to an output (json or csv) file
    """
    # filenames
    input_filename: str = field(init=True)
    output_filename: str = field(init=True, default='extracted_requirements.json')
    
    # regex pattern for text segmentation
    re_document_split_pattern: str = field(init=False, default='(?s)(?<=Section).*?(?=Section|$)')
    # regex pattern for section number extraction
    re_section_number_pattern: str = field(init=True, default='Section ([\d]{1,2})')
        
    
    def _check_input_parameters(self) -> bool:
        """
        Checks input parameters
        
        :returns: True if all checks passed, False otherwise
        """
        try:
            assert isinstance(self.input_filename, str), f"Input parameter 'input_filename' must be str, got {type(self.input_filename)}"
            assert Path(self.input_filename).exists(), f"Input file '{self.input_filename}' was not found"

            assert isinstance(self.output_filename, str), f"Input parameter 'output_filename' must be str, got {type(self.output_filename)}"
            assert Path(self.output_filename).suffix in ['.json', '.csv'], "Input parameter 'output_filename' must be either a json or a csv file"
            
            logger.info('Input parameters checked')
            return True
        except Exception as e:
            logger.error(repr(e))
            return False

    
    def _extract_sections_from_file(self, filename: str) -> List[str]:
        """
        Read input file and extract all sections from it using regex pattern

        :param filename: A path to the file with regulations text
        :returns: a list of extracted sections as plain strings
        """
        # Read regulations file
        try:
            with open(filename, 'r') as f:
                self.full_text = f.read()
        except Exception as e:
            logger.error(repr(e))
            return []

        sections = ['Section' + text for text in re.findall(self.re_document_split_pattern, self.full_text)]
        if len(sections) == 0:
            logger.warning("No sections were extracted from input file!")
        else:
            logger.info(f"{len(sections)} sections were extracted")

        return sections
    

    def _extract_section_number(self, section_text: str, section_number_pattern: str) -> Optional[int]:
        """
        Extract section number from section text following regex pattern provided

        :param section_text: Full section text
        :param section_number_pattern: Regex pattern to get section number
        :returns: Section number (integer) or None if not found
        """
        section_number = re.findall(section_number_pattern, section_text)[0] if re.search(section_number_pattern, section_text) else None
        if section_number:
            return int(section_number)
        else:
            logger.warning("Section number was not extracted. Check regex pattern provided")
            return None

    
    def simulate_llm_summary(self, section_text: str) -> str:
        """
        This function simulates LLM responce to summarize a given text.
        Current implementation normalizes input text by removing all special symbols and returns the text words in reversed order.

        :param section_text: A given text of a section
        :returns: Simulated output from LLM
        """
        # Remove all special symbols
        normalized_text = re.sub('[^\w\s.,!@#$%^&*()=+~`-]', ' ', section_text)
        # Remove all new line symbols
        normalized_text = re.sub('\n', ' ', normalized_text)
        # Remove multiple spaces
        normalized_text = re.sub('[\s]+', ' ', normalized_text)
        # Remove extra spaces
        normalized_text = normalized_text.strip()

        # Split text into words and return them in reversed order
        output_text = ' '.join(normalized_text.split()[::-1])
        return output_text


    def extract_and_summarize(self) -> None:
        """
        Extract sections from a given regulations file and apply LLM to generate summaries of each section
        
        :returns: None, all results are saved as either a json or a csv file
        """
        # Check input parameters
        if not self._check_input_parameters():
            return
        
        # Remove output file if exists
        if Path(self.output_filename).exists():
            Path(self.output_filename).unlink()

        # Extract sections
        sections = self._extract_sections_from_file(self.input_filename)

        # Extract section numbers
        section_numbers = [self._extract_section_number(section_text, self.re_section_number_pattern) for section_text in sections]

        # Extract summaries
        summaries = [self.simulate_llm_summary(section_text) for section_text in sections]

        output = pd.DataFrame({
            'section_number': section_numbers,
            'original_text': sections,
            'summarized_requirements': summaries
        })

        if Path(self.output_filename).suffix == '.json':
            output.to_json(self.output_filename)
        else:
            output.to_csv(self.output_filename, index=False)


if __name__ == "__main__":
    app()