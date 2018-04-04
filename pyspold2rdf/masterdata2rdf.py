# python3
"""Transform Ecoinvent's MasterData into RDF and JSON-LD

Notes:
-----

This package allows to transform Ecoinvent's MasterData (*.xml) into RDF and JSON-LD.
The package is compatible with the IEO ontology[1].

[1]: https://github.com/cfrancois7/IEO-ontology

"""
import argparse
import xml.etree.ElementTree as Xml
from os.path import splitext, abspath
from rdflib import Graph, Literal, Namespace, RDF, RDFS
from unit import ecoinvent_units


# Constant
registries={'http://www.EcoInvent.org/EcoSpold02':
               {'reg_id': 'de659012-50c4-4e96-b54a-fc781bf987ab',
                'label': 'EcoInvent'}}
BFO = OBI = IAO = Namespace('http://purl.obolibrary.org/obo/')
IEO = Namespace('http://www.isterre.fr/ieo/')
ECO = Namespace('http://www.EcoInvent.org/EcoSpold02'.lower() + '#')
SERVICE = OBI.OBI_0001173
MATERIAL_ENTITY = BFO.BFO_0000040
IAO.denotes = IAO.IAO_0000219
BFO.has_part = BFO.BFO_0000051
BFO.part_of = BFO.BFO_0000050
LCA_DATABASE = IEO.IEO_0000043
LCA_REGISTRY = IEO.IEO_0000044


def define_registry(func):
    """Define the type and the label of the database version and the registry.
    """
    def func_wrapper(graph: Graph, xml_root: Xml, registry: dict,
                     namespaces: dict, tag: str):
        # crid_reg: CRID registry, e.g Ecoinvent
        crid_reg = registry['reg_id']
        crid_reg_label = registry['label']
        graph.add((LCA_REGISTRY, RDFS.label,
                   Literal('life cycle database registry', lang='en')))
        graph.add((ECO[crid_reg], RDF.type, LCA_REGISTRY))
        graph.add((ECO[crid_reg], RDFS.label, Literal(crid_reg_label)))
        # Database identifier, e.g. EcoInvent3.1
        major_release = xml_root.attrib['majorRelease']
        minor_release = xml_root.attrib['minorRelease']
        database_version = f'v{major_release}_{minor_release}'
        graph.add((LCA_DATABASE, RDFS.label,
                   Literal('life cycle database version', lang='en')))
        database_id = crid_reg+database_version
        database_label = crid_reg_label+f'v{major_release}.{minor_release}'
        graph.add((ECO[database_id], RDF.type, LCA_DATABASE))
        graph.add((ECO[database_id], RDFS.label,
                   Literal(database_label)))
        graph.add((ECO[database_id], IAO.denotes, ECO[crid_reg]))
        graph.add((IAO.denotes, RDFS.label,
                   Literal('denotes', lang='en')))
        graph.add((BFO.BFO_0000040, RDFS.label,
                   Literal('material entity', lang='en')))
        graph.add((ECO[database_id], RDFS.label,
                   Literal(database_label)))
        graph.add((OBI.OBI_0001173, RDFS.label,
                   Literal('service', lang='en')))
        graph.add((BFO.has_part, RDFS.label,
                   Literal('has part', lang='en')))
        graph.add((BFO.part_of, RDFS.label,
                   Literal('part of', lang='en')))
        graph = func(graph, xml_root, registry, namespaces, tag)
        return graph
    return func_wrapper


@define_registry
def act2graph(graph: Graph, xml_root: Xml, registry: dict,
              namespaces: dict, tag: str) -> Graph:
    """ Transform activityName tag into RDF graph.

    The function transforms the Activity MasterData into identifier. The output
    is a RDF graph that represents a part of the Ecoinvent nomenclature
    structured with The IEO ontology. The output represents the centrally
    registrered identifier (CRID) by the database version and the activity name
    identifier, e.g. ecoinvent3.0:88d6c0aa-0053-4367-b0be-05e4b49ff3c5 for the
    copper production, primary.
    Variables:
    - graph: the graph to update
    - xml_root: the root of the xml file
    - registry: dictionary containing the reference/info of the data registry
    - tag: string containing the namespace tag
    - namespaces: dictionary containing the namespaces with tags
    """
    # crid_reg: CRID registry, e.g Ecoinvent
    crid_reg = registry['reg_id']
    crid_reg_label = registry['label']
    # Database identifier, e.g. EcoInvent3.1
    major_release = xml_root.attrib['majorRelease']
    minor_release = xml_root.attrib['minorRelease']
    database_version = f'v{major_release}_{minor_release}'
    database_label = f'{crid_reg_label}{major_release}.{minor_release}'
    database_id = crid_reg+database_version
    for activity_name in xml_root.findall(tag, namespaces):
        activity_name_id = activity_name.attrib['id']
        crid = activity_name_id+database_version
        graph.add((ECO[crid], RDF.type, ECO.activityId))
        graph.add((ECO[activity_name_id], RDF.type, ECO.activity_name))
        # Define the property relation between the symbols of the CRID
        graph.add((ECO[crid], BFO.has_part, ECO[database_id]))
        graph.add((ECO[database_id], BFO.part_of, ECO[crid]))
        graph.add((ECO[crid], BFO.has_part, ECO[activity_name_id]))
        graph.add((ECO[activity_name_id], BFO.part_of, ECO[crid]))
        # Define the labels with the different languages
        xml_ns = namespaces['xml']
        for name in activity_name.findall('eco:name', namespaces):
            lang = name.attrib['{'+xml_ns+'}lang']
            activity_label = name.text
            crid_label = f'{database_label}:{activity_label}'
            graph.add((ECO[crid], RDFS.label, Literal(crid_label, lang=lang)))
            graph.add((ECO[activity_name_id],
                       RDFS.label,
                       Literal(activity_label, lang=lang)))
    return graph


@define_registry
def inter2graph(graph: Graph, xml_root: Xml,
                registry: dict, namespaces: dict, tag: str) -> Graph:
    """Transform intermediateExchange tag into RDF graph.

    The function transforms the IntermediateExchange MasterData into identifier.
    The output is a RDF graph that represents a part of the Ecoinvent
    nomenclature structured with the IEO ontology. The output represents the
    centrally registrered identifier (CRID) by the database version and the
    intermediate name identifier,
    e.g. ecoinvent3.0:fbb039f7-f9cc-46d2-b631-313ddb125c1a for the copper.
    TODO: link the intermediary exchange nomenclature to the material products
    and its property. In reality, the intermediary exchange name denotes a
    product that has some quality (properties). It's wrong to link direclty
    the nomenclature to the property.
    Variables:
    - graph: the graph to update
    - xml_root: the root of the xml file
    - registry: dictionary containing the reference/info of the data registry
    - tag: string containing the namespace tag
    - namespaces: dictionary containing the namespaces with tags
    """
    crid_reg = registry['reg_id']
    crid_reg_label = registry['label']
    # Database identifier, e.g. EcoInvent3.1
    major_release = xml_root.attrib['majorRelease']
    minor_release = xml_root.attrib['minorRelease']
    database_version = f'v{major_release}_{minor_release}'
    database_label = f'{crid_reg_label}{major_release}.{minor_release}'
    database_id = crid_reg+database_version
    for inter_exch in xml_root.findall(tag, namespaces):
        inter_exch_id = inter_exch.attrib['id']
        crid = inter_exch_id+database_version
        graph.add((ECO[crid], RDF.type, ECO.interm_exch_Id))
        graph.add((ECO[inter_exch_id], RDF.type, ECO.interm_exch_name))
        # Define the property relation between the symbols of the CRID
        graph.add((ECO[crid], BFO.has_part, ECO[database_id]))
        graph.add((ECO[database_id], BFO.part_of, ECO[crid]))
        graph.add((ECO[crid], BFO.has_part, ECO[inter_exch_id]))
        graph.add((ECO[inter_exch_id], BFO.part_of, ECO[crid]))
        # Define the labels with the different languages
        xml_ns = namespaces['xml']
        # t_prod as 'type product'
        product_id = inter_exch_id+'t_prod'
        graph.add((ECO[inter_exch_id], IAO.denotes, ECO[product_id]))
        for name in inter_exch.findall('eco:name', namespaces):
            lang = name.attrib['{'+xml_ns+'}lang']
            inter_exch_label = name.text
            crid_label = f'{database_label}:{inter_exch_label}'
            graph.add((ECO[crid], RDFS.label, Literal(crid_label, lang=lang)))
            graph.add((ECO[inter_exch_id],
                       RDFS.label,
                       Literal(inter_exch_label, lang=lang)))
            graph.add((ECO[product_id], RDFS.label,
                       Literal(inter_exch_label, lang=lang)))
        # Detect if the product is a good (and not a service)
        # Only goods have property
        # But all goods don't have property
        if inter_exch.find('eco:property', namespaces) is not None:
            # Create the types
            graph.add((ECO[product_id], RDF.type, MATERIAL_ENTITY))
        elif inter_exch.find('eco:unitName', namespaces).text\
          in ecoinvent_units['good']:
            graph.add((ECO[product_id], RDF.type, MATERIAL_ENTITY))
        elif inter_exch.find('eco:unitName', namespaces).text\
          in ecoinvent_units['service']:
            graph.add((ECO[product_id], RDF.type, SERVICE))
        else:
            graph.add((ECO[product_id], RDF.type, IEO.to_sort))
    return graph
        # TODO: get the quality (property) and link them to the good


@define_registry
def elem2graph(graph: Graph, xml_root: Xml,
               registry: dict, namespaces: dict, tag: str) -> Graph:
    """ Transform elementaryExchange into RDF graph.

    The function transforms the ElementaryExchange MasterData into identifier.
    The output is a RDF graph representing a part of the Ecoinvent nomenclature
    structured with the IEO ontology. The output represents the centrally
    registrered identifier (CRID) by the database version and the elementary
    name identifier, e.g. ecoinvent3.0:f9749677-9c9f-4678-ab55-c607dfdc2cb9 for
    the Carbon dioxide, fossil.
    TODO: link the elementary exchange nomenclature to the material substance
    and its property. In reality, the elementary exchange name denotes a
    substance that has some quality (properties). It's wrong to link direclty
    the nomenclature to the property.
    Variables:
    - graph: the graph to update
    - xml_root: the root of the xml file
    - registry: dictionary containing the reference/info of the data registry
    - tag: string containing the namespace tag
    - namespaces: dictionary containing the namespaces with tags
    """
    crid_reg = registry['reg_id']
    crid_reg_label = registry['label']
    # Database identifier, e.g. EcoInvent3.1
    major_release = xml_root.attrib['majorRelease']
    minor_release = xml_root.attrib['minorRelease']
    database_version = f'v{major_release}_{minor_release}'
    database_label = f'{crid_reg_label}{major_release}.{minor_release}'
    database_id = crid_reg+database_version
    for elem_exch in xml_root.findall(tag, namespaces):
        elem_exch_id = elem_exch.attrib['id']
        crid = elem_exch_id+database_version
        graph.add((ECO[crid], RDF.type, ECO.elementary_exchange_id))
        graph.add((ECO[elem_exch_id], RDF.type, ECO.elem_exch_name))
        # Define the property relation between the symbols of the CRID
        graph.add((ECO[crid], BFO.has_part, ECO[database_id]))
        graph.add((ECO[database_id], BFO.part_of, ECO[crid]))
        graph.add((ECO[crid], BFO.has_part, ECO[elem_exch_id]))
        graph.add((ECO[elem_exch_id], BFO.part_of, ECO[crid]))
        # Define the labels with the different languages
        xml_ns = namespaces['xml']
        product_id = elem_exch_id+'t_prod'
        graph.add((ECO[elem_exch_id], IAO.denotes, ECO[product_id]))
        for name in elem_exch.findall('eco:name', namespaces):
            lang = name.attrib['{'+xml_ns+'}lang']
            compartment = "eco:compartment/eco:compartment[@xml:lang='"+lang+"']"
            subcompartment = "eco:compartment/eco:subcompartment[@xml:lang='"+lang+"']"
            compartment_label = elem_exch.find(compartment, namespaces)
            subcompartment_label = elem_exch.find(subcompartment, namespaces)
            if (compartment_label and subcompartment_label) is not None:
                elem_exch_label = f"{name.text}, in {compartment_label.text}, {subcompartment_label.text}"
                crid_label = f'{database_label}:{elem_exch_label}'
                graph.add((ECO[crid], RDFS.label, Literal(crid_label, lang=lang)))
                graph.add((ECO[elem_exch_id],
                           RDFS.label,
                           Literal(elem_exch_label, lang=lang)))
                graph.add((ECO[product_id], RDFS.label,
                           Literal(elem_exch_label, lang=lang)))
        if elem_exch.find('eco:property', namespaces) is not None:
            # Create the types
            graph.add((ECO[product_id], RDF.type, MATERIAL_ENTITY))
        elif elem_exch.find('eco:unitName', namespaces).text\
          in ecoinvent_units['good']:
            graph.add((ECO[product_id], RDF.type, MATERIAL_ENTITY))
        else:
            graph.add((ECO[product_id], RDF.type, IEO.to_sort))
    return graph


def xml2graph(path: str) -> Graph:
    """ Tranform the xml into a rdfgraph. The input is an MasterData file and
    the output is a RDF graph. It detects the content of the masterData
    (activity, intermediary exchange, elementary exchange...) and applies it
    the proper function."""
    graph = Graph()
    tree = Xml.parse(path)
    root = tree.getroot()
    # define the dictionary of function
    masterDataTransf = {'eco:activityName': act2graph,
                        'eco:intermediateExchange': inter2graph,
                        'eco:elementaryExchange': elem2graph,
                        }
    # get the namespace
    file_namespace = root.tag.split('}')[0].strip('{')
    # verify the namespace is known, otherwise provide them
    if file_namespace in registries:
        registry = registries[file_namespace]
    else:
        print("""\
        The namespace of the file and the registry of the data are unknown.
        Please update the masterdata2rdf.py file and abort the execution with
        ctrl-c, or provide them: """)
        registry['reg_id'] = input('What is the ID of the registry? ').lower()
        registry['label'] = input('What is the registry label?')
    ns = {'eco': file_namespace,
          'xml': 'http://www.w3.org/XML/1998/namespace'}
    # detect what MasterData file it is with the tags (ActivityName,
    # ElementaryExchange, IntermediaryExchange, etc.) and apply the proper
    # functions.
    for tag in masterDataTransf.keys():
        if root.find(tag, ns):
            print(f"The file contains {tag.split(':')[1]} nomenclature data")
            # call the proper function in function of the tag
            graph = masterDataTransf[tag](graph=graph, xml_root=root,
                                          registry=registry, namespaces=ns,
                                          tag=tag)
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
    description = """Transform Ecoinvent's MasterData into Graph and export
    it to the proper format."""
    usage = """ Usage:
    -----

    Command in shell:
    $ python3 xml2rdf.py [OPTION] file1.xml

    Arguments:
    file1.xml: the Ecoinvent's MasterData file to transforme. It has to
    respect the Ecospold2 format for MasterData.

    Options:
    -output, -o"""
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
        help="the Ecoinvent's MasterData file to transforme.")
    parser.add_argument(
        "output_path",
        metavar='path_to_output_file',
        nargs='?',
        type=str,
        default=False,
        help="the path of the output (default: input_name.format)")
    args = parser.parse_args()
    input_path = args.input_path[0]
    graph = xml2graph(input_path)
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
