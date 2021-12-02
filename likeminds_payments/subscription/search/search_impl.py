from typing import Union

from subscription.search.constants import SearchIndices
from subscription.search.search_manager import SearchManager
from elasticsearch_dsl import Search

from subscription.utility.number_utilities import NumberUtilities
from subscription.utility.time_utilities import TimeUtilities


class SearchImpl(SearchManager):

    def __init__(self, member_id: str, search_term: str, search_field: str = None,
                 page: int = 1, page_size: int = 50, community_id: str = None):
        self.member_id = member_id
        self.search_term = search_term
        self.search_field = search_field
        self.page = page
        self.page_size = page_size
        self.community_id = community_id

    def get_member_id(self) -> Union[str, int]:
        return self.member_id

    def set_member_id(self, member_id: Union[str, int]) -> None:
        self.member_id = member_id

    def get_search_term(self) -> str:
        return self.search_term.lower()

    def get_search_field(self) -> str:
        return self.search_field.lower()

    def get_page_number(self) -> int:
        return self.page

    def get_page_size(self) -> int:
        return self.page_size

    def get_community_id(self) -> Union[str, int]:
        return NumberUtilities.get_integer_from_string(self.community_id)

    def search_plan(self):
        res = Search.from_dict(self._get_plan_search_ngram_query_dict()).execute()

        search_response = [hit.to_dict() for hit in res]

        return search_response

    def search_history(self):
        res = Search().from_dict(self._get_history_search_ngram_query_dict()).execute()

        search_response = set([hit['user_id'] for hit in res])
        search_response = list(search_response)

        return search_response

    def _get_plan_search_ngram_query_dict(self, index=SearchIndices.SUBSCRIPTION_PLAN):
        """
        @return: dict
        """
        return {
            "from": self.get_page_size() * (self.get_page_number() - 1),
            "size": self.get_page_size(),
            "sort": {
                "_score": {
                    "order": "desc"
                }
            },
            "query": {
                "bool": {
                    "must": [{
                        "query_string": {
                            "query": f"*{self.get_search_term()}*",
                            "fields": [
                                f"{self.get_search_field()}"
                            ]
                        }
                    }],
                    "filter": [
                        {"term": {"community_id": f"{self.get_community_id()}"}},
                        {"term": {"_index": index.value}}
                    ]
                }
            }
        }

    def _get_history_search_ngram_query_dict(self, index=SearchIndices.SUBSCRIPTION_HISTORY):
        """
        @return: dict
        """
        return {
            "from": self.get_page_size() * (self.get_page_number() - 1),
            "size": self.get_page_size(),
            "sort": {
                "_score": {
                    "order": "desc"
                }
            },
            "query": {
                "bool": {
                    "must": [{
                        "query_string": {
                            "query": f"*{self.get_search_term()}*",
                            "fields": [
                                f"{self.get_search_field()}"
                            ]
                        }
                    }, {
                        "range": {
                            "end_date": {
                                "lt": TimeUtilities.current_time_in_milliseconds()
                            }
                        }
                    }],
                    "filter": [
                        {"term": {"community_id": f"{self.get_community_id()}"}},
                        {"term": {"_index": index.value}}
                    ]
                }
            }
        }
