from typing import Dict, List, Tuple, Generator
import pandas as pd

def process_kopeika_algorihm_output(indirect_shares, df_companies: pd.DataFrame) -> Dict[Tuple[str], Dict[Tuple[str, str], float]]:
    """
    Yields a tuple containing a list of strings representing a company and a dictionary representing the beneficiaries of the company.
    
    The dictionary contains the identifiers of the beneficiaries as keys and the shares of the company they own as values.
    
    The beneficiaries are considered to be those who own more than 25% of the shares of the company.
    """
    dict_companies = {}
    
    for _, company_id, ogrn, inn, full_name in df_companies.itertuples():
        dict_companies[company_id] = (ogrn, inn, full_name)
    
    res = {}
    for company_id, shares in indirect_shares.items():
        company = dict_companies[company_id]
        beneficiaries = {beneficiary_identifier : share
            for beneficiary_identifier, share in shares.items()
            if share > 0.25}
        res[company] = (beneficiaries)
    return res
            

def beneficiares_to_writable_block(beneficiares: Dict[Tuple[str, str], float]) -> Generator[Tuple[str, ...], None, None]:
    """
    Converts a dictionary of beneficiaries to a writable block format.

    This function takes a dictionary where the keys are tuples of (inn, fio)
    and the values are percentages. It yields each beneficiary's information
    as a list of strings, including the inn, fio (split into separate names),
    and the percentage rounded to two decimal places.

    :param beneficiares: A dictionary with keys as tuples (inn, fio) and values
                         as percentages.
    :return: A generator yielding lists of strings representing each beneficiary's
             information.
    """
    for (inn, fio), percent in beneficiares.items():
        info = ('', inn, *fio.split(), str(round(percent, 2)))
        yield info


def create_writable_results(beneficiares_of_companies: Dict[Tuple[str], Dict[Tuple[str, str], float]]) -> Generator[Tuple[str, ...], None, None]:
    """
    Converts a dictionary of companies to a writable block format.

    This function takes a dictionary where the keys are OGRN and the values are
    dictionaries of beneficiaries. It yields each company's information as a list
    of strings, including the company ID, OGRN, INN, and name. Then, it yields
    each beneficiary's information in the same format as
    `beneficiares_to_writable_block`.

    :param beneficiares_of_companies: A dictionary with keys as OGRN and values
                                       as dictionaries of beneficiaries.
    :param legal_db: A dictionary with OGRN as keys and values as lists of
                     [company_id, inn, company_name].
    :return: A generator yielding lists of strings representing companies and
             their beneficiaries.
    """
    for company_info, beneficiares in beneficiares_of_companies.items():
        yield company_info
        yield from beneficiares_to_writable_block(beneficiares)
        
def write_to_tsv(data: Generator[Tuple[str, ...], None, None], filename):
    """
    Writes a list of lists to a TSV file.

    :param data: A list of lists, where each sublist is a row of data.
    :param filename: The name of the file to write the data to.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(['\t'.join(row) for row in data]))

def postprocess_default(indirect_shares, df_companies: pd.DataFrame, final_filepath):
    beneficiares_of_companies = process_kopeika_algorihm_output(indirect_shares, df_companies)
    write_to_tsv(create_writable_results(beneficiares_of_companies), final_filepath)
