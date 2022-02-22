import abc


class PlanManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'create_plan') and callable(subclass.create_plan)) and
                (hasattr(subclass, 'fetch_plan') and callable(subclass.fetch_plan)) and
                (hasattr(subclass, 'delete_plan') and callable(subclass.delete_plan)) and
                (hasattr(subclass, 'create_event_plan') and callable(subclass.create_event_plan)) and
                (hasattr(subclass, 'fetch_event_plan') and callable(subclass.fetch_event_plan)) and
                (hasattr(subclass, 'update_event_plan') and callable(subclass.update_event_plan)) and
                (hasattr(subclass, 'fetch_sample_plan_category') and callable(subclass.fetch_sample_plan_category)) and
                (hasattr(subclass, 'fetch_sample_plans') and callable(subclass.fetch_sample_plans)) and
                (hasattr(subclass, 'fetch_event_plan_with_cohort_plan') and
                 callable(subclass.fetch_event_plan_with_cohort_plan)) or
                NotImplemented)

    @abc.abstractmethod
    def create_plan(self) -> dict:
        """
        create a new plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_plan(self) -> dict:
        """
        fetch all the plans of a community
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_plan(self) -> dict:
        """
        delete an existing plan
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_event_plan(self, req_body, member_id) -> dict:
        """
        create a plan for event
        """

        raise NotImplementedError

    @abc.abstractmethod
    def fetch_event_plan(self, chatroom_ids) -> dict:
        """
        return events of chatroom ids
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update_event_plan(self, req_body, member_id) -> dict:
        """
        update a plan for event
        """

        raise NotImplementedError

    @abc.abstractmethod
    def fetch_sample_plan_category(self) -> dict:
        """
        return samples plan categories
        """

        raise NotImplementedError

    @abc.abstractmethod
    def fetch_sample_plans(self, category_id) -> dict:
        """
        return samples plans
        """

        raise NotImplementedError

    @abc.abstractmethod
    def fetch_event_plan_with_cohort_plan(self) -> dict:
        """
        returns event plans with cohort plans
        """

        raise NotImplementedError
