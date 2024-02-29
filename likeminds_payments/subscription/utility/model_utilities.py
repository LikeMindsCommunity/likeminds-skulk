class ModelUtilities:
    """class contains utility functions for models"""

    @staticmethod
    def model_update(model, filter_dict, update_dict):
        update_status = model.objects.filter(**filter_dict).update(**update_dict)

        return update_status

    @staticmethod
    def get_model_filter(model, filter_dict):
        return model.objects.filter(**filter_dict)

    @staticmethod
    def is_model_filter_exists(model, filter_dict):
        return model.objects.filter(**filter_dict).exists()

    @staticmethod
    def get_model_instance_or_none(model, pk):

        instance = None
        try:
            instance = model.objects.get(id=pk)

        except Exception:

            pass

        return instance

    @staticmethod
    def paginate_queryset(queryset, page, paginate_by):

        offset = (page - 1) * paginate_by

        return queryset[offset: offset + paginate_by]

    @staticmethod
    def delete_record_in_model(model, filter_dict):
        return model.objects.filter(**filter_dict).delete()

    @staticmethod
    def divide_chunks(model_list, chunk_size=1000):

        for i in range(0, len(model_list), chunk_size):
            yield model_list[i:i + chunk_size]

    @staticmethod
    def bulk_create_instances(model, model_list, chunk_size=1000):

        bulk_create_list = list(ModelUtilities.divide_chunks(model_list, chunk_size))

        for instance_list in bulk_create_list:
            model.objects.bulk_create(instance_list)

    @staticmethod
    def bulk_update_instances(model, model_list, fields, chunk_size=1000):

        if not fields:
            return

        bulk_create_list = list(ModelUtilities.divide_chunks(model_list, chunk_size))

        for instance_list in bulk_create_list:
            model.objects.bulk_update(instance_list, fields, chunk_size)
