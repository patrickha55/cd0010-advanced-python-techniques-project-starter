"""A database encapsulating collections of near-Earth objects and their close approaches.

A `NEODatabase` holds an interconnected data set of NEOs and close approaches.
It provides methods to fetch an NEO by primary designation or by name, as well
as a method to query the set of close approaches that match a collection of
user-specified criteria.

Under normal circumstances, the main module creates one NEODatabase from the
data on NEOs and close approaches extracted by `extract.load_neos` and
`extract.load_approaches`.

You'll edit this file in Tasks 2 and 3.
"""
from typing import Generator
from models import NearEarthObject, CloseApproach
from filters import AttributeFilter


class NEODatabase:
    """A database of near-Earth objects and their close approaches.

    A `NEODatabase` contains a collection of NEOs and a collection of close
    approaches. It additionally maintains a few auxiliary data structures to
    help fetch NEOs by primary designation or by name and to help speed up
    querying for close approaches that match criteria.
    """

    def __init__(self, neos: list[NearEarthObject], approaches: list[CloseApproach]):
        """Create a new `NEODatabase`.

        As a precondition, this constructor assumes that the collections of NEOs
        and close approaches haven't yet been linked - that is, the
        `.approaches` attribute of each `NearEarthObject` resolves to an empty
        collection, and the `.neo` attribute of each `CloseApproach` is None.

        However, each `CloseApproach` has an attribute (`._designation`) that
        matches the `.designation` attribute of the corresponding NEO. This
        constructor modifies the supplied NEOs and close approaches to link them
        together - after it's done, the `.approaches` attribute of each NEO has
        a collection of that NEO's close approaches, and the `.neo` attribute of
        each close approach references the appropriate NEO.

        :param neos: A collection of `NearEarthObject`s.
        :param approaches: A collection of `CloseApproach`es.
        """
        self._neos = neos
        self._approaches = approaches

        # Create a lookup table using NEO's designation as key and the index of a NEO in a list as value.
        self._designation_to_index: dict[str, int] = {}

        for i, neo in enumerate(self._neos):
            self._designation_to_index[neo.designation] = i

        for approach in self._approaches:
            if approach.neo is None:
                if approach._designation in self._designation_to_index:
                    # Get a neo by getting an index in the lookup table above through the approach's designation and pass it to the _neos list.
                    approach.neo = self._neos[self._designation_to_index[approach._designation]]
                    # Append the approach above to the neo's approaches' list.
                    approach.neo.approaches.append(approach)

        # Auxiliary data structures to help speed up the inspect and query time.
        self._designation_to_neo = {
            neo.designation.lower(): neo for neo in self._neos
        }
        self._name_to_neo = {
            neo.name.lower(): neo for neo in self._neos if neo.name is not None
        }

    def get_neo_by_designation(self, designation: str) -> NearEarthObject | None:
        """Find and return an NEO by its primary designation.

        If no match is found, return `None` instead.

        Each NEO in the data set has a unique primary designation, as a string.

        The matching is exact - check for spelling and capitalization if no
        match is found.

        :param designation: The primary designation of the NEO to search for.
        :return: The `NearEarthObject` with the desired primary designation, or `None`.
        """
        return self._designation_to_neo.get(designation.strip().lower(), None)

    def get_neo_by_name(self, name: str) -> NearEarthObject | None:
        """Find and return an NEO by its name.

        If no match is found, return `None` instead.

        Not every NEO in the data set has a name. No NEOs are associated with
        the empty string nor with the `None` singleton.

        The matching is exact - check for spelling and capitalization if no
        match is found.

        :param name: The name, as a string, of the NEO to search for.
        :return: The `NearEarthObject` with the desired name, or `None`.
        """
        return self._name_to_neo.get(name.strip().lower(), None)

    def query(self, filters: set[AttributeFilter] = ()) -> Generator[CloseApproach, CloseApproach, CloseApproach]:
        """Query close approaches to generate those that match a collection of filters.

        This generates a stream of `CloseApproach` objects that match all of the
        provided filters.

        If no arguments are provided, generate all known close approaches.

        The `CloseApproach` objects are generated in internal order, which isn't
        guaranteed to be sorted meaningfully, although is often sorted by time.

        :param filters: A collection of filters capturing user-specified criteria.
        :return: A stream of matching `CloseApproach` objects.
        """
        for approach in self._approaches:
            if len(filters) == 0:
                yield approach

            result = False

            for filter in filters:

                if filter(approach):
                    result = True
                else:
                    result = False
                    break

            if result is False:
                continue

            yield approach
