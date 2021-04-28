from waflib.Node import Nod3
from typing import List


def get_dependent_files_for_metadata(metadata: Nod3) -> List[Nod3]:
    """
        todo: Probably want to pull foreign key related table URLs out here too.

        todo: How do we deal with URLs which are true `http://some-domain/some-file.csv` how do we ensure
         the build is only triggered when those files change?
         should we override the signature method and do manual hashes of those URL's files?
    """
    implicit_dependencies = []
    csvw_schema = metadata.read_json()
    if "url" in csvw_schema:
        implicit_dependencies.append(csvw_schema["url"])
    elif "tables" in csvw_schema:
        for table in csvw_schema["tables"]:
            if "url" in table:
                implicit_dependencies.append(table["url"])

    return [metadata.parent.find_node(d) for d in implicit_dependencies]
