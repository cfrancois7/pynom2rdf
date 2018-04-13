# python3
"""Transform ISIC classifications into RDF and JSON-LD

Notes:
-----

This package allows to transform ISIC classification (*.txt) into RDF and JSON-LD.
It can transform the ISIC classification into centrally registered identifier
(CRID) and into classes.
The package is compatible with the IEO ontology[1].

[1]: https://github.com/cfrancois7/IEO-ontology

"""
import argparse
from os.path import splitext, abspath
from rdflib import Graph, Literal, Namespace, RDF, RDFS
from pandas import read_csv, DataFrame
from ieo_types import nom_graph


ISIC = Namespace('https://unstats.un.org/unsd/cr/registry/')
BFO = OBI = IAO = Namespace('http://purl.obolibrary.org/obo/')
IEO = Namespace('http://www.isterre.fr/ieo/')
IAO.denotes = IAO.IAO_0000219
BFO.has_part = BFO.BFO_0000051
BFO.part_of = BFO.BFO_0000050
# Industrial activity classification (IAC)
REGISTRY_VERSION = IEO.IEO_0000043
REF_ACTIVITY = IEO.IEO_0000065
ACTITIVY_CRID = IEO.IEO_0000066
STAT_REGISTRY = IEO.IEO_0000071


def sup_spe_charact(text: str):
    for char in ['\\','`','*',' ','>','#','+','-','.','!','$','\'']:
        if char in text:
            text = text.replace(char, "_")
        elif char in ['{','}','[',']','(',')']:
            text = text.replace(char, "")
    return text


def verify_version() -> int:
    try:
        version_number = int(input('What is the version number of the ISIC Rev classification? :'))
    except:
        print('The version has to be an integer')
        version_number = verify_version()
    return version_number


def isic2crid(data: DataFrame) -> Graph:
    graph = nom_graph()
    crid_reg = 'ISIC'
    crid_reg_label = 'International Standard Industrial Classification'
    version = str(verify_version())
    graph.add((STAT_REGISTRY, RDFS.label,
               Literal('statistical classification registry', lang='en')))
    graph.add((ISIC[crid_reg], RDF.type, STAT_REGISTRY))
    graph.add((ISIC[crid_reg], RDFS.label, Literal(crid_reg_label)))
    database_id = 'ISIC_Rev'+version
    database_label = 'International Standard Industrial Classification (ISIC) Rev'+version
    graph.add((REGISTRY_VERSION, RDFS.label,
               Literal('registry version', lang='en')))
    graph.add((ISIC[database_id], RDF.type, REGISTRY_VERSION))
    graph.add((ISIC[database_id], RDFS.label,
               Literal(database_label)))
    graph.add((ISIC[database_id], IAO.denotes, ISIC[crid_reg]))
    graph.add((IAO.denotes, RDFS.label,
               Literal('denotes', lang='en')))
    classification_label = f'ISIC Rev{version} identifier'
    graph.add((ISIC.classification, RDFS.label, Literal(classification_label, lang='en')))
    graph.add((ISIC.classification, RDFS.subClassOf, ACTITIVY_CRID))
    ind_sector_label = classification_label+' label'
    graph.add((ISIC.industrial_sector, RDFS.subClassOf, REF_ACTIVITY))
    graph.add((ISIC.industrial_sector, RDFS.label, Literal(ind_sector_label, lang='en')))
    for code in data.index:
        activity_label = data.loc[code][0]
        crid = f'{database_id}_{code}'
        crid_label = f'{database_id}:{code} {activity_label}'
        activity_id = sup_spe_charact(activity_label)
        graph.add((ISIC[activity_id], RDF.type, ISIC.industrial_sector))
        graph.add((ISIC[activity_id], RDFS.label, Literal(activity_label, lang='en')))
        graph.add((ISIC[crid], RDFS.label, Literal(crid_label, lang='en')))
        graph.add((ISIC[crid], RDF.type, ISIC.classification))
        graph.add((ISIC[crid], RDFS.label, Literal(crid_label, lang='en')))
        graph.add((ISIC[crid], BFO.has_part, ISIC[database_id]))
        graph.add((ISIC[database_id], BFO.part_of, ISIC[crid]))
        graph.add((ISIC[crid], BFO.has_part, ISIC[activity_id]))
        graph.add((ISIC[activity_id], BFO.part_of, ISIC[crid]))
    return graph


def avoid_overwrite(output_path: str) -> str:
    """ The function prevents the overwriting of the source file by the
    output."""
    message = """" The path for the output and the input file is the same.
    The input file is going to be overwritten. Are you sure to overwrite
    the input file? (Yes/No): """
    answer = input(message).lower()
    if answer in ['yes', 'y']:
        return output_path
    elif answer in ('no', 'n'):
        message = " What is the new path? (absolute or relative path): "
        new_path = input(message)
        return new_path
    else:
        print('Error. The expected answer is Yes or No.')
        return avoid_overwrite(output_path)


def main():
    description = """Transform ISIC classification registry into Graph and export
    it to the proper format."""
    usage = """ Usage:
    -----

    Command in shell:
    $ python3 isic2rdf.py [OPTION] file1.xml

    Arguments:
    file1.xml: the Ecoinvent's MasterData file to transforme. It has to
    respect the Ecospold2 format for MasterData.

    Options:
    -output, -o path of the output file
    --format, -f format of the output"""
    # create the parser
    parser = argparse.ArgumentParser(
        description=description,
        usage=usage)
    parser.add_argument(
        "--format", '-f',
        nargs=1,
        choices=['json-ld', 'xml', 'n3', 'nt'],
        default=['xml'],
        help='the output format of the file (default: Xml)')
    parser.add_argument(
        "input_path",
        metavar='path_to_input_file',
        nargs=1,
        type=str,
        help="the ISIC's file to transforme.")
    parser.add_argument(
        "output_path",
        metavar='path_to_output_file',
        nargs='?',
        type=str,
        default=False,
        help="the path of the output (default: input_name.format)")
    args = parser.parse_args()
    input_path = args.input_path[0]
    try:
        data = read_csv(input_path, index_col=0)
    except:
        raise('Error in the input file. Impossible to open it. '\
              'The format expected is [code][label]')
    graph = isic2crid(data)
    if not args.output_path:
        path = abspath(args.input_path[0])
        name_file = splitext(path)[0]
        new_ext = {'json-ld': '.json', 'xml': '.rdf', 'n3': '.n3',
                   'nt': '.nt'}
        new_ext = new_ext[args.format[0]]
        output_path = name_file+new_ext
    else:
        output_path = args.output_path
    if input_path == output_path:
        output_path = avoid_overwrite(output_path)
    graph.serialize(output_path, format=args.format[0])


if __name__ == "__main__":
    main()
