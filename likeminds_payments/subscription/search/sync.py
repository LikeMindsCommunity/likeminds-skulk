from elasticsearch_dsl import Search, UpdateByQuery
from elasticsearch import Elasticsearch


from .constants import SearchIndices

from django_elasticsearch_dsl.registries import registry

from ..plans.models import SubscriptionPlan
from ..utility.model_utilities import ModelUtilities

client = Elasticsearch()


class ElasticSearchSync:

    @staticmethod

    def bulk_update_documents(index: SearchIndices, query_dict: dict):
        """
        @param index: enum SearchIndices
        @param query_dict: dict
        @return: None
        @description: bulk updates all documents with matching condition
        """
        s = UpdateByQuery(index=index.value).update_from_dict(query_dict)
        s.execute()

    @staticmethod
    def delete_documents(index: SearchIndices, query_dict: dict):
        """
        @param index: enum SearchIndices
        @param query_dict: dict
        @return: None
        @description: delete documents from elastic search permanently
        """
        s = Search(index=index.value).update_from_dict(query_dict)
        s.delete()

    @staticmethod
    def update_document(instance_list: list):
        """
        @param instance_list: list of instances
        @return: None
        @description: updates documents in elastic search
        """
        for instance in instance_list:
            registry.update(instance)

    @staticmethod
    def delete_subscription_plan(plan_id: str):
        """
        @param plan_id:
        @return: None
        @description: Delete a subscription plan
        """

        query_dict = ElasticSearchQueryHelper.get_plan_with_plan_id(plan_id=plan_id)
        ElasticSearchSync.delete_documents(index=SearchIndices.SUBSCRIPTION_PLAN,
                                           query_dict=query_dict)

    @staticmethod
    def update_subscription_plan(plan_id: str):
        """
        @param plan_id:
        @return: None
        @description: Updates a subscription plan after removal of any user
        """

        instances = ModelUtilities.get_model_filter(SubscriptionPlan, {'plan_id': plan_id})

        if not instances:
            return

        ElasticSearchSync.update_document(instance_list=instances)


class ElasticSearchQueryHelper:

    @staticmethod
    def get_plan_with_plan_id(plan_id: str):
        """
        @param plan_id:
        @return: dict
        @sql: where plan_id = plan_id
        """
        return {
            "query": {
                "match": {
                    "plan_id": plan_id
                }
            }
        }
